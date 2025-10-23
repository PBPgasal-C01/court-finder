from math import radians, sin, cos, sqrt, atan2
import requests
from django.core.cache import cache

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two coordinates in kilometers using Haversine formula
    """
    R = 6371  # Earth radius in kilometers
    
    lat1_rad = radians(float(lat1))
    lon1_rad = radians(float(lon1))
    lat2_rad = radians(float(lat2))
    lon2_rad = radians(float(lon2))
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c


def is_in_indonesia(latitude, longitude):
    """
    Check if coordinates are within Indonesia bounds (rough approximation)
    Indonesia bounds: lat -11 to 6, lon 95 to 141
    """
    lat = float(latitude)
    lon = float(longitude)
    return -11 <= lat <= 6 and 95 <= lon <= 141


def geocode_address(address):
    """
    Convert address to coordinates using Nominatim (OpenStreetMap)
    Returns: {'latitude': float, 'longitude': float} or None if not found
    """
    cache_key = f'geocode_{address}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address + ', Indonesia',  # Force Indonesia search
            'format': 'json',
            'limit': 1,
            'countrycodes': 'id',  # Restrict to Indonesia
        }
        headers = {
            'User-Agent': 'CourtFinder/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        results = response.json()
        if results:
            result = results[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            # Validate coordinates are in Indonesia
            if is_in_indonesia(lat, lon):
                coords = {'latitude': lat, 'longitude': lon}
                cache.set(cache_key, coords, 60 * 60 * 24)  # Cache for 24 hours
                return coords
        return None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None