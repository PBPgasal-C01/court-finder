from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from .models import Court, Bookmark, Province
from .serializers import CourtSerializer, ProvinceSerializer
from .utils import haversine_distance, geocode_address, is_in_indonesia

@require_http_methods(["GET"])
def court_finder(request):
    """Main court finder page"""
    provinces = Province.objects.all()
    court_types = Court.COURT_TYPES
    
    context = {
        'provinces': provinces,
        'court_types': court_types,
        'default_lat': -6.2088,  # Jakarta
        'default_lon': 106.8456,
        'is_authenticated': request.user.is_authenticated,  # ← TAMBAH INI
    }
    return render(request, 'court_filter/court_finder.html', context)


@api_view(['POST'])
def geocode_api(request):
    """Convert address to coordinates (Indonesia only)"""
    address = request.data.get('address')
    
    if not address:
        return Response(
            {'error': 'Alamat harus diisi'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    coords = geocode_address(address)
    if coords:
        return Response(coords, status=status.HTTP_200_OK)
    else:
        return Response(
            {'error': 'Alamat tidak ditemukan di Indonesia'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def search_courts(request):
    """Search courts with filters and location-based radius"""
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    provinces = request.data.getlist('provinces[]') or request.data.getlist('provinces')
    price_min = request.data.get('price_min')
    price_max = request.data.get('price_max')
    court_types = request.data.getlist('court_types[]') or request.data.getlist('court_types')
    bookmarked_only = request.data.get('bookmarked_only') == 'true'
    radius = 10  # km
    
    if not latitude or not longitude:
        return Response(
            {'error': 'Latitude dan longitude diperlukan'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate coordinates are in Indonesia
    if not is_in_indonesia(latitude, longitude):
        return Response(
            {'error': 'Lokasi harus berada di Indonesia'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Start with active courts
    queryset = Court.objects.filter(is_active=True)
    
    # Apply province filter if specified
    if provinces:
        queryset = queryset.filter(provinces__id__in=provinces).distinct()
    
    # Apply price filter
    if price_min:
        queryset = queryset.filter(price_per_hour__gte=Decimal(price_min))
    if price_max:
        queryset = queryset.filter(price_per_hour__lte=Decimal(price_max))
    
    # Apply court type filter
    if court_types:
        queryset = queryset.filter(court_type__in=court_types)
    
    # Apply bookmark filter (only if user is authenticated)
    if bookmarked_only and request.user.is_authenticated:
        bookmarked_court_ids = Bookmark.objects.filter(
            user=request.user
        ).values_list('court_id', flat=True)
        queryset = queryset.filter(id__in=bookmarked_court_ids)
    
    # Calculate distances and filter by radius
    courts_with_distance = []
    latitude = float(latitude)
    longitude = float(longitude)
    
    for court in queryset:
        distance = haversine_distance(
            latitude, longitude,
            court.latitude, court.longitude
        )
        
        if distance <= radius:
            courts_with_distance.append((court, distance))
    
    # Sort by distance
    courts_with_distance.sort(key=lambda x: x[1])
    courts = [court for court, _ in courts_with_distance]
    
    if not courts:
        return Response(
            {'error': 'Tidak ada lapangan dalam jarak 10km dari lokasi Anda', 'courts': []},
            status=status.HTTP_200_OK
        )
    
    # Add distance to context for serializer
    distance_map = {court.id: distance for court, distance in courts_with_distance}
    
    serializer = CourtSerializer(
        courts,
        many=True,
        context={'request': request, 'distance': distance_map}
    )
    
    return Response({'courts': serializer.data, 'count': len(courts)}, status=status.HTTP_200_OK)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def toggle_bookmark(request, court_id):
    """Toggle bookmark for a court (POST to add, DELETE to remove)"""
    try:
        court = Court.objects.get(id=court_id, is_active=True)
    except Court.DoesNotExist:
        return Response(
            {'error': 'Lapangan tidak ditemukan'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'POST':
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            court=court
        )
        return Response(
            {'message': 'Lapangan berhasil di-bookmark', 'bookmarked': True},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    elif request.method == 'DELETE':
        deleted, _ = Bookmark.objects.filter(
            user=request.user,
            court=court
        ).delete()
        
        if deleted:
            return Response(
                {'message': 'Bookmark dihapus', 'bookmarked': False},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Bookmark tidak ditemukan'},
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def get_provinces(request):
    """Get all provinces"""
    provinces = Province.objects.all()
    serializer = ProvinceSerializer(provinces, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
