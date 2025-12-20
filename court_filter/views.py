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
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.permissions import AllowAny
import json

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

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # Tidak melakukan apa-apa (Bypass CSRF)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication]) # Biar User Login gak kena blokir CSRF
@permission_classes([AllowAny])
def search_courts(request):
    """
    Search courts with dynamic logic:
    - If lat/lon are provided: search by 10km radius.
    - If lat/lon are NOT provided: search by filters across the entire database.
    """
    # FIX: request.data adalah dict, bukan QueryDict
    # Ambil data dengan .get() untuk single value atau langsung akses untuk list
    
    # Untuk court_types yang bisa multiple

    data = request.data

    # Jika request.data kosong (karena masalah Content-Type), coba parse body manual
    if not data and request.body:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            pass

    # 1. Ambil court_types
    court_types_data = data.get('court_types[]') or data.get('court_types') # Pakai 'data', bukan 'request.data'
    if court_types_data:
        if isinstance(court_types_data, list):
            court_types = court_types_data
        else:
            court_types = [court_types_data]
    else:
        court_types = []
    
    # 2. Ambil parameter lain (Gunakan 'data')
    province_name = data.get('province')
    price_min = data.get('price_min')
    price_max = data.get('price_max')
    bookmarked_only = str(data.get('bookmarked_only')).lower() == 'true'
    
    # Mulai dengan queryset dasar
    queryset = Court.objects.filter(is_active=True)
    
    # --- Terapkan SEMUA filter non-lokasi terlebih dahulu ---
    
    if province_name:
        queryset = queryset.filter(provinces__name=province_name)
    
    if price_min:
        queryset = queryset.filter(price_per_hour__gte=Decimal(price_min))
    if price_max:
        queryset = queryset.filter(price_per_hour__lte=Decimal(price_max))
    
    if court_types:
        types_to_search = list(court_types)
        
        if 'futsal' in types_to_search:
            types_to_search.append('futsal')
        
        if 'other' not in types_to_search:
            queryset = queryset.filter(court_type__in=types_to_search)
    
    if bookmarked_only and request.user.is_authenticated:
        bookmarked_court_ids = Bookmark.objects.filter(user=request.user).values_list('court_id', flat=True)
        queryset = queryset.filter(id__in=bookmarked_court_ids)
    
    # --- LOGIKA UTAMA: Cek apakah ini pencarian RADIUS atau FILTER ---
    
    final_courts_data = []
    
    if 'latitude' in data and 'longitude' in data: # Pakai 'data'
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        radius_km = 10
        
        courts_with_distance = []
        for court in queryset:
            distance = haversine_distance(latitude, longitude, float(court.latitude), float(court.longitude))
            if distance <= radius_km:
                courts_with_distance.append((court, distance))
        
        # Urutkan berdasarkan jarak terdekat
        courts_with_distance.sort(key=lambda x: x[1])
        
        # Siapkan data untuk response
        for court, distance in courts_with_distance:
            is_bookmarked = request.user.is_authenticated and Bookmark.objects.filter(user=request.user, court=court).exists()
            final_courts_data.append({
                'id': str(court.id),  # Convert UUID to string
                'name': court.name,
                'address': court.address,
                'court_type': court.court_type,
                'location_type': court.location_type,
                'latitude': float(court.latitude),
                'longitude': float(court.longitude),
                'price_per_hour': float(court.price_per_hour),
                'phone_number': court.phone_number,
                'description': court.description,
                'provinces': [{'id': p.id, 'name': p.name} for p in court.provinces.all()],
                'is_bookmarked': is_bookmarked,
                'distance': round(distance, 2)
            })
    else:
        # TIPE 2: PENCARIAN FILTER
        queryset = queryset.order_by('name')
        
        for court in queryset:
            is_bookmarked = request.user.is_authenticated and Bookmark.objects.filter(user=request.user, court=court).exists()
            final_courts_data.append({
                'id': str(court.id),  # Convert UUID to string
                'name': court.name,
                'address': court.address,
                'court_type': court.court_type,
                'location_type': court.location_type,
                'latitude': float(court.latitude),
                'longitude': float(court.longitude),
                'price_per_hour': float(court.price_per_hour),
                'phone_number': court.phone_number,
                'description': court.description,
                'provinces': [{'id': p.id, 'name': p.name} for p in court.provinces.all()],
                'is_bookmarked': is_bookmarked,
                'distance': None
            })

    return Response({
        'courts': final_courts_data,
        'count': len(final_courts_data)
    }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST']) # Cukup POST saja
@authentication_classes([CsrfExemptSessionAuthentication])
@permission_classes([IsAuthenticated])
def toggle_bookmark(request, court_id):
    try:
        court = Court.objects.get(id=court_id, is_active=True)
    except Court.DoesNotExist:
        return Response({'error': 'Lapangan tidak ditemukan'}, status=404)

    # --- LOGIKA SMART TOGGLE ---
    
    # 1. Cari apakah bookmark sudah ada?
    bookmark = Bookmark.objects.filter(user=request.user, court=court).first()

    if bookmark:
        # KALO UDAH ADA -> HAPUS
        bookmark.delete()
        return Response({
            'message': 'Bookmark dihapus', 
            'bookmarked': False # <-- Info penting buat Flutter: "Matiin lampunya!"
        }, status=200)
    else:
        # KALO BELUM ADA -> TAMBAH
        Bookmark.objects.create(user=request.user, court=court)
        return Response({
            'message': 'Bookmark ditambahkan', 
            'bookmarked': True # <-- Info penting buat Flutter: "Nyalain lampunya!"
        }, status=200)

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