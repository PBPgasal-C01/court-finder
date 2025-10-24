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
from django.shortcuts import get_object_or_404
from urllib.parse import unquote

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
    """
    Search courts with dynamic logic:
    - If lat/lon are provided: search by 10km radius.
    - If lat/lon are NOT provided: search by filters across the entire database.
    """
    # Ambil semua parameter filter dari request
    provinces = request.data.getlist('provinces[]') or request.data.getlist('provinces')
    province_name = request.data.get('province') # Untuk dropdown
    price_min = request.data.get('price_min')
    price_max = request.data.get('price_max')
    court_types = request.data.getlist('court_types[]')
    bookmarked_only = request.data.get('bookmarked_only') == 'true'
    
    # Mulai dengan queryset dasar
    queryset = Court.objects.filter(is_active=True)
    
    # --- Terapkan SEMUA filter non-lokasi terlebih dahulu ---
    # Ini penting untuk memperkecil jumlah data yang akan di-loop nanti
    
    if province_name: # Untuk dropdown baru
        queryset = queryset.filter(provinces__name=province_name)
    
    if price_min:
        queryset = queryset.filter(price_per_hour__gte=Decimal(price_min))
    if price_max:
        queryset = queryset.filter(price_per_hour__lte=Decimal(price_max))
    
    if court_types:
        types_to_search = list(court_types)
        
        if 'sutsal' in types_to_search:
            types_to_search.append('futsal')
        
        if 'other' not in types_to_search:
            queryset = queryset.filter(court_type__in=types_to_search)
    
    if bookmarked_only and request.user.is_authenticated:
        bookmarked_court_ids = Bookmark.objects.filter(user=request.user).values_list('court_id', flat=True)
        queryset = queryset.filter(id__in=bookmarked_court_ids)
        
    # --- LOGIKA UTAMA: Cek apakah ini pencarian RADIUS atau FILTER ---
    
    final_courts_data = []
    
    if 'latitude' in request.data and 'longitude' in request.data:
        # TIPE 1: PENCARIAN RADIUS (menggunakan loop Python dan haversine)
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
        radius_km = 10
        
        courts_with_distance = []
        for court in queryset:
            distance = haversine_distance(latitude, longitude, court.latitude, court.longitude)
            if distance <= radius_km:
                courts_with_distance.append((court, distance))
        
        # Urutkan berdasarkan jarak terdekat
        courts_with_distance.sort(key=lambda x: x[1])
        
        # Siapkan data untuk response
        for court, distance in courts_with_distance:
            is_bookmarked = request.user.is_authenticated and Bookmark.objects.filter(user=request.user, court=court).exists()
            final_courts_data.append({
                'id': court.id, 'name': court.name, 'address': court.address,
                'court_type': court.court_type, 'latitude': court.latitude, 'longitude': court.longitude,
                'price_per_hour': court.price_per_hour, 'is_bookmarked': is_bookmarked,
                'distance': round(distance, 2)
            })
            
    else:
        # TIPE 2: PENCARIAN FILTER (tanpa menghitung jarak)
        # Queryset sudah difilter di atas, tinggal diurutkan
        queryset = queryset.order_by('name')
        
        # Siapkan data untuk response
        for court in queryset:
            is_bookmarked = request.user.is_authenticated and Bookmark.objects.filter(user=request.user, court=court).exists()
            final_courts_data.append({
                'id': court.id, 'name': court.name, 'address': court.address,
                'court_type': court.court_type, 'latitude': court.latitude, 'longitude': court.longitude,
                'price_per_hour': court.price_per_hour, 'is_bookmarked': is_bookmarked,
                'distance': None # Jarak tidak relevan di sini
            })

    return Response({
        'courts': final_courts_data,
        'count': len(final_courts_data)
    }, status=status.HTTP_200_OK)

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

def court_detail_view(request, court_name):
    # Decode nama dari URL
    decoded_name = unquote(court_name)
    
    # Get court by name
    court = get_object_or_404(Court, name=decoded_name)
    
    context = {
        'court': court,
        'is_authenticated': request.user.is_authenticated,
    }
    
    return render(request, 'court_filter/court_detail.html', context)