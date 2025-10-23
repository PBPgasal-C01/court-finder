from django.test import TestCase
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Court, Bookmark, Province
from django.core.cache import cache
import requests
from court_filter.utils import haversine_distance, is_in_indonesia, geocode_address

User = get_user_model()


class CourtFinderViewTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Siapkan data yang tidak berubah untuk semua tes.
        """
        # 1. Buat User
        cls.user = User.objects.create_user(username='testuser', password='testpassword')

        # 2. Buat Provinsi
        cls.prov_jakarta = Province.objects.create(name='DKI Jakarta')
        cls.prov_jawa_barat = Province.objects.create(name='Jawa Barat')

        # 3. Buat Lapangan
        
        # Lapangan dekat (Jakarta 1)
        cls.court_jakarta_1 = Court.objects.create(
            name="Lapangan Basket Monas",
            latitude=Decimal('-6.2000'),
            longitude=Decimal('106.8000'),
            price_per_hour=Decimal('150000'),
            court_type='basketball',
            is_active=True
        )
        cls.court_jakarta_1.provinces.add(cls.prov_jakarta)

        # Lapangan dekat (Jakarta 2 - Futsal)
        cls.court_jakarta_2 = Court.objects.create(
            name="Lapangan Futsal Senayan",
            latitude=Decimal('-6.2100'),
            longitude=Decimal('106.8100'),
            price_per_hour=Decimal('250000'),
            court_type='futsal',
            is_active=True
        )
        cls.court_jakarta_2.provinces.add(cls.prov_jakarta)

        # Lapangan jauh (Bekasi - Tennis) - SESUAI REVISI ANDA
        cls.court_tennis_bekasi = Court.objects.create(
            name="Lapangan Tennis Bekasi",
            latitude=Decimal('-6.2383'),  # Koordinat Bekasi
            longitude=Decimal('106.9756'),
            price_per_hour=Decimal('120000'),
            court_type='tennis',
            is_active=True
        )
        cls.court_tennis_bekasi.provinces.add(cls.prov_jawa_barat)

        # Lapangan tidak aktif
        cls.court_inactive = Court.objects.create(
            name="Lapangan Tutup",
            latitude=Decimal('-6.2000'),
            longitude=Decimal('106.8000'),
            price_per_hour=Decimal('50000'),
            court_type='basketball',
            is_active=False
        )
        cls.court_inactive.provinces.add(cls.prov_jakarta)
        
        # 4. Buat Bookmark
        cls.bookmark = Bookmark.objects.create(user=cls.user, court=cls.court_jakarta_1)

        # 5. Data umum
        cls.jakarta_coords = {'latitude': -6.2088, 'longitude': 106.8456}
    
        cls.URL_FINDER = reverse('court_filter:court_finder')
        cls.URL_GEOCODE = reverse('court_filter:geocode_api')
        cls.URL_SEARCH = reverse('court_filter:search_courts')
        cls.URL_PROVINCES = reverse('court_filter:get_provinces')

    
    def test_court_finder_view_anonymous(self):
        """Tes halaman utama finder (GET) sebagai anonymous."""
        response = self.client.get(self.URL_FINDER)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'court_filter/court_finder.html')
        self.assertIn('provinces', response.context)
        self.assertIn('court_types', response.context)
        self.assertFalse(response.context['is_authenticated'])
        self.assertIn(self.prov_jakarta, response.context['provinces'])

    def test_court_finder_view_authenticated(self):
        """Tes halaman utama finder (GET) sebagai user login."""
        self.client.force_login(self.user)
        response = self.client.get(self.URL_FINDER)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.context['is_authenticated'])

    @patch('court_filter.views.geocode_address')
    def test_geocode_api_success(self, mock_geocode):
        """Tes geocode API (POST) berhasil."""
        mock_geocode.return_value = {'latitude': -6.2, 'longitude': 106.8}
        
        data = {'address': 'Monas, Jakarta'}
        response = self.client.post(self.URL_GEOCODE, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['latitude'], -6.2)
        mock_geocode.assert_called_with('Monas, Jakarta')

    @patch('court_filter.views.geocode_address')
    def test_geocode_api_not_found(self, mock_geocode):
        """Tes geocode API (POST) jika alamat tidak ditemukan."""
        mock_geocode.return_value = None
        
        data = {'address': 'asdfghjkl'}
        response = self.client.post(self.URL_GEOCODE, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_geocode_api_no_address(self):
        """Tes geocode API (POST) jika 'address' tidak dikirim."""
        data = {'address': ''}
        response = self.client.post(self.URL_GEOCODE, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Alamat harus diisi', response.data['error'])

    @patch('court_filter.views.is_in_indonesia', return_value=True)
    @patch('court_filter.views.haversine_distance')
    def test_search_courts_success_basic(self, mock_haversine, mock_is_in_indo):
        """Tes pencarian dasar (POST) di Jakarta, radius 10km."""
        
        def side_effect(lat1, lon1, lat2, lon2):
            if lat2 == self.court_jakarta_1.latitude: return 2.5
            if lat2 == self.court_jakarta_2.latitude: return 1.5
            # Cek lapangan bekasi (di luar radius 10km)
            if lat2 == self.court_tennis_bekasi.latitude: return 30.0 
            return 1000
        mock_haversine.side_effect = side_effect

        response = self.client.post(self.URL_SEARCH, self.jakarta_coords)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        
        self.assertEqual(response.data['courts'][0]['name'], self.court_jakarta_2.name)
        self.assertEqual(response.data['courts'][1]['name'], self.court_jakarta_1.name)
        
        for court in response.data['courts']:
            self.assertNotEqual(court['name'], self.court_inactive.name)

    def test_search_courts_no_coords(self):
        """Tes pencarian (POST) tanpa latitude/longitude."""
        data = {'latitude': ''}
        response = self.client.post(self.URL_SEARCH, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Latitude dan longitude diperlukan', response.data['error'])

    @patch('court_filter.views.is_in_indonesia', return_value=False)
    def test_search_courts_outside_indonesia(self, mock_is_in_indo):
        """Tes pencarian (POST) jika koordinat di luar Indonesia."""
        data = {'latitude': 1.0, 'longitude': 1.0}
        response = self.client.post(self.URL_SEARCH, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Lokasi harus berada di Indonesia', response.data['error'])

    @patch('court_filter.views.is_in_indonesia', return_value=True)
    @patch('court_filter.views.haversine_distance', return_value=1.0)
    def test_search_courts_filter_province(self, mock_haversine, mock_is_in_indo):
        """Tes pencarian (POST) dengan filter provinsi."""
        data = {
            **self.jakarta_coords,
            'provinces[]': [self.prov_jawa_barat.id]  # Cari di Jawa Barat
        }
        response = self.client.post(self.URL_SEARCH, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        # Cek lapangan bekasi
        self.assertEqual(response.data['courts'][0]['name'], self.court_tennis_bekasi.name)

    @patch('court_filter.views.is_in_indonesia', return_value=True)
    @patch('court_filter.views.haversine_distance', return_value=1.0)
    def test_search_courts_filter_price(self, mock_haversine, mock_is_in_indo):
        """Tes pencarian (POST) dengan filter harga."""
        data = {
            **self.jakarta_coords,
            'price_max': '200000'  # Maks 200rb (Jkt 1 & Bekasi)
        }
        response = self.client.post(self.URL_SEARCH, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        names = {c['name'] for c in response.data['courts']}
        self.assertIn(self.court_jakarta_1.name, names)
        # Cek lapangan bekasi
        self.assertIn(self.court_tennis_bekasi.name, names)

    @patch('court_filter.views.is_in_indonesia', return_value=True)
    @patch('court_filter.views.haversine_distance', return_value=1.0)
    def test_search_courts_filter_court_type(self, mock_haversine, mock_is_in_indo):
        """Tes pencarian (POST) dengan filter jenis lapangan."""
        data = {
            **self.jakarta_coords,
            'court_types[]': ['futsal'] 
        }
        response = self.client.post(self.URL_SEARCH, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['courts'][0]['name'], self.court_jakarta_2.name)

    @patch('court_filter.views.is_in_indonesia', return_value=True)
    @patch('court_filter.views.haversine_distance', return_value=1.0)
    def test_search_courts_filter_bookmarked_authenticated(self, mock_haversine, mock_is_in_indo):
        """Tes pencarian (POST) filter bookmark (user login)."""
        self.client.force_login(self.user)
        data = {
            **self.jakarta_coords,
            'bookmarked_only': 'true'
        }
        response = self.client.post(self.URL_SEARCH, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['courts'][0]['name'], self.court_jakarta_1.name)

    @patch('court_filter.views.is_in_indonesia', return_value=True)
    @patch('court_filter.views.haversine_distance', return_value=1.0)
    def test_search_courts_filter_bookmarked_anonymous(self, mock_haversine, mock_is_in_indo):
        """Tes pencarian (POST) filter bookmark (anonymous), harus diabaikan."""
        data = {
            **self.jakarta_coords,
            'bookmarked_only': 'true'
        }

        response = self.client.post(self.URL_SEARCH, data) 
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)

    def test_toggle_bookmark_add_new(self):
        """Tes bookmark (POST) lapangan baru oleh user login."""
        self.client.force_login(self.user)
        self.assertFalse(Bookmark.objects.filter(user=self.user, court=self.court_jakarta_2).exists())

        url = reverse('court_filter:toggle_bookmark', kwargs={'court_id': self.court_jakarta_2.id})
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['bookmarked'], True)
        self.assertTrue(Bookmark.objects.filter(user=self.user, court=self.court_jakarta_2).exists())

    def test_toggle_bookmark_add_existing(self):
        """Tes bookmark (POST) lapangan yang sudah di-bookmark."""
        self.client.force_login(self.user)
        self.assertTrue(Bookmark.objects.filter(user=self.user, court=self.court_jakarta_1).exists())

        url = reverse('court_filter:toggle_bookmark', kwargs={'court_id': self.court_jakarta_1.id})
        response = self.client.post(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bookmarked'], True)

    def test_toggle_bookmark_delete(self):
        """Tes hapus bookmark (DELETE) oleh user login."""
        self.client.force_login(self.user)
        self.assertTrue(Bookmark.objects.filter(user=self.user, court=self.court_jakarta_1).exists())

        url = reverse('court_filter:toggle_bookmark', kwargs={'court_id': self.court_jakarta_1.id})
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['bookmarked'], False)
        self.assertFalse(Bookmark.objects.filter(user=self.user, court=self.court_jakarta_1).exists())

    def test_toggle_bookmark_delete_non_existent(self):
        """Tes hapus bookmark (DELETE) yang tidak ada."""
        self.client.force_login(self.user)
        url = reverse('court_filter:toggle_bookmark', kwargs={'court_id': self.court_jakarta_2.id})
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_toggle_bookmark_invalid_court(self):
        """Tes bookmark (POST/DELETE) untuk court ID yang tidak ada."""
        self.client.force_login(self.user)
        url = reverse('court_filter:toggle_bookmark', kwargs={'court_id': 9999})
        
        response_post = self.client.post(url, format='json')
        response_delete = self.client.delete(url, format='json')
        
        self.assertEqual(response_post.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_provinces(self):
        """Tes API (GET) semua provinsi."""
        response = self.client.get(self.URL_PROVINCES, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        province_names = {p['name'] for p in response.data}
        self.assertIn('DKI Jakarta', province_names)
        self.assertIn('Jawa Barat', province_names)
    
    def test_court_detail_view_success(self):
        """Tes halaman detail (GET) dengan nama yang valid."""
        url = reverse('court_filter:court_detail', kwargs={'court_name': self.court_jakarta_1.name})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'court_filter/court_detail.html')
        self.assertEqual(response.context['court'], self.court_jakarta_1)

    def test_court_detail_view_not_found(self):
        """Tes halaman detail (GET) dengan nama yang tidak ada (404)."""
        url = reverse('court_filter:court_detail', kwargs={'court_name': 'Lapangan Hantu'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_court_detail_view_with_url_encoding(self):
        """Tes halaman detail (GET) jika nama mengandung spasi (URL encoding)."""
        spaced_name_court = Court.objects.create(
            name="Lapangan Keren Pakai Spasi", 
            latitude=0, longitude=0, price_per_hour=0
        )
        
        url = reverse('court_filter:court_detail', kwargs={'court_name': spaced_name_court.name})
        self.assertIn('%20', url)
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.context['court'], spaced_name_court)

class UtilsTests(TestCase):
    
    def setUp(self):
        cache.clear()

    def test_haversine_distance(self):
        """
        Tes kalkulasi jarak haversine.
        """
        self.assertEqual(haversine_distance(10, 10, 10, 10), 0)
        jakarta_lat, jakarta_lon = -6.17539, 106.82715
        bandung_lat, bandung_lon = -6.9175, 107.6191
        
        distance = haversine_distance(jakarta_lat, jakarta_lon, bandung_lat, bandung_lon)
        self.assertAlmostEqual(distance, 120.26, delta=1) # Toleransi 1 km

        distance_str = haversine_distance(str(jakarta_lat), str(jakarta_lon), str(bandung_lat), str(bandung_lon))
        self.assertAlmostEqual(distance_str, 120.26, delta=1)

    def test_is_in_indonesia(self):
        """
        Tes pengecekan batas wilayah Indonesia.
        """
        self.assertTrue(is_in_indonesia(-6.2, 106.8))
        
        # 2. Di batas (Sabang)
        self.assertTrue(is_in_indonesia(5.8, 95.3))
        
        # 3. Di batas (Merauke)
        self.assertTrue(is_in_indonesia(-8.4, 140.3))
        
        # 4. Di luar
        self.assertFalse(is_in_indonesia(6.1, 100))
        self.assertFalse(is_in_indonesia(51.5, -0.12))

    @patch('court_filter.utils.requests.get')
    def test_geocode_address_success(self, mock_requests_get):
        """
        Tes geocode berhasil, API dipanggil, dan hasil di-cache.
        """
        address = "Monas, Jakarta"
        cache_key = f'geocode_{address}'

        mock_api_result = [{
            'lat': '-6.175392', 
            'lon': '106.827153'
        }]
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_result
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        self.assertIsNone(cache.get(cache_key))

        coords = geocode_address(address)

        expected_coords = {'latitude': -6.175392, 'longitude': 106.827153}
        self.assertEqual(coords, expected_coords)

        mock_requests_get.assert_called_once()

        self.assertEqual(cache.get(cache_key), expected_coords)

    @patch('court_filter.utils.requests.get')
    def test_geocode_address_cached(self, mock_requests_get):
        """
        Tes geocode berhasil mengambil dari cache, API TIDAK dipanggil.
        """
        address = "GBK, Jakarta"
        cache_key = f'geocode_{address}'
        expected_coords = {'latitude': -6.2183, 'longitude': 106.8023}

        cache.set(cache_key, expected_coords)

        coords = geocode_address(address)

        self.assertEqual(coords, expected_coords)

        mock_requests_get.assert_not_called()

    @patch('court_filter.utils.requests.get')
    def test_geocode_address_api_failure(self, mock_requests_get):
        """
        Tes geocode gagal jika API mengembalikan error (misal: 500).
        """
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.RequestException
        mock_requests_get.return_value = mock_response

        coords = geocode_address("Alamat Gagal")

        self.assertIsNone(coords)

    @patch('court_filter.utils.requests.get')
    def test_geocode_address_not_found(self, mock_requests_get):
        """
        Tes geocode gagal jika API tidak menemukan alamat (hasil '[]').
        """

        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        coords = geocode_address("asdfghjkl")

        self.assertIsNone(coords)

    @patch('court_filter.utils.requests.get')
    def test_geocode_address_outside_indonesia(self, mock_requests_get):
        """
        Tes geocode jika API (secara keliru) mengembalikan hasil di luar Indonesia.
        """
        mock_api_result = [{
            'lat': '48.8584', 
            'lon': '2.2945'
        }]
        mock_response = MagicMock()
        mock_response.json.return_value = mock_api_result
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        coords = geocode_address("Paris, France")

        self.assertIsNone(coords)