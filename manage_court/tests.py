from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Court, Province, Facility
import json

# Dapatkan model User yang sedang aktif (dari app autentikasi)
User = get_user_model()

class ManageCourtTests(TestCase):
    def setUp(self):
        """Siapkan data palsu yang akan kita gunakan untuk testing."""
        # User Fake
        self.user_owner_1 = User.objects.create_user(
            username='owner1', 
            password='password123',
            email='owner1@test.com'  
        )
        self.user_owner_2 = User.objects.create_user(
            username='owner2', 
            password='password123',
            email='owner2@test.com' 
        )
        
        # 2. Fake "Data Master" 
        self.province = Province.objects.create(name='DKI Jakarta')
        self.facility = Facility.objects.create(name='Toilet')

        # 3. Fake Court
        self.court_milik_owner_1 = Court.objects.create(
            owner=self.user_owner_1,
            name='Lapangan Owner 1',
            address='Alamat 1',
            court_type='futsal',
            price_per_hour=150000,
            province=self.province
        )
        
        self.court_milik_owner_2 = Court.objects.create(
            owner=self.user_owner_2,
            name='Lapangan Owner 2',
            address='Alamat 2',
            court_type='badminton',
            price_per_hour=200000,
            province=self.province
        )
        
        # 4. Fake Browser 
        self.client = Client()

    # TES Halaman Utama (Guest vs User)
    def test_show_manage_court_as_guest(self):
        """
        Tes: Apakah GUEST (belum login) melihat pesan "You have to login"
        dan TIDAK melihat lapangan?
        """
        # Visit page
        response = self.client.get(reverse('manage_court:show_manage_court'))
        
        self.assertEqual(response.status_code, 200) # 1. Cek kl succes
        self.assertContains(response, 'You have to login') # 2. Cek ada pesan login
        self.assertNotContains(response, 'Lapangan Owner 1') # 3. Cek lapangan TIDAK MUNCUL

    def test_show_manage_court_as_owner(self):
        """
        Tes: Apakah OWNER (sudah login) HANYA melihat lapangannya sendiri?
        """
        # "Login" browser palsu kita sebagai owner 1
        self.client.force_login(self.user_owner_1)
        
        # Kunjungi halaman utama
        response = self.client.get(reverse('manage_court:show_manage_court'))
        
        self.assertEqual(response.status_code, 200) # 1. Cek halaman sukses dibuka
        self.assertNotContains(response, 'You have to login') # 2. Cek pesan login TIDA_K MUNCUL
        self.assertContains(response, 'Lapangan Owner 1') # 3. Cek lapangan DIA MUNCUL
        self.assertNotContains(response, 'Lapangan Owner 2') # 4. Cek lapangan milik owner 2 TIDA_K MUNCUL

    # TES Page Detail
    def test_court_detail_public(self):
        """
        Tes: Apakah GUEST bisa melihat halaman detail publik?
        (View 'court_detail' kamu tidak pakai @login_required)
        """
        url = reverse('manage_court:court_detail', args=[self.court_milik_owner_1.pk])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200) # 1. Cek halaman sukses dibuka
        self.assertContains(response, 'Lapangan Owner 1') # 2. Cek nama lapangan muncul
        self.assertContains(response, 'Alamat 1') # 3. Cek alamatnya muncul


    # TES AJAX (Create)    
    def test_add_court_ajax_unauthenticated(self):
        """
        Tes: Apakah GUEST yang mencoba "Create" (POST) akan ditolak?
        """
        url = reverse('manage_court:add_court_ajax')
        # kirim data (POST) sbg guest
        response = self.client.post(url, {'name': 'Lapangan Bajakan'})
        
        # @login_required akan me-redirect (302) ke halaman login
        self.assertEqual(response.status_code, 302) 

    def test_add_court_ajax_authenticated(self):
        """
        Tes: Apakah OWNER (sudah login) bisa "Create" data via AJAX?
        """
        # Login sebagai owner 1
        self.client.force_login(self.user_owner_1)
        
        url = reverse('manage_court:add_court_ajax')
        
        # fake data untuk dikirim
        post_data = {
            'name': 'Lapangan Baru Milik Owner 1',
            'address': 'Alamat baru',
            'court_type': 'futsal',
            'price_per_hour': 250000,
            'province': self.province.pk, # Kirim ID provinsinya
            'facilities': [self.facility.pk] # Kirim list ID fasilitas
        }
        
        # Kirim data POST. 
        # 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest' BISA ditambahkan jika view-mu mengecek request.is_ajax()
        response = self.client.post(url, post_data)
        
        # Cek apakah server response "Sukses" (200)
        self.assertEqual(response.status_code, 200)
        
        # Cek apakah responnya adalah JSON yang benar
        data = response.json()
        self.assertEqual(
            data['status'], 
            'success', 
            f"Form was invalid. Errors: {data.get('errors')}"
        )
        
        # Cek apakah datanya bnr masuk ke database dan dimiliki oleh owner 1
        self.assertTrue(Court.objects.filter(
            name='Lapangan Baru Milik Owner 1',
            owner=self.user_owner_1
        ).exists())

    # TES AJAX (Delete)
    def test_delete_court_by_wrong_owner(self):
        """
        Tes: Apakah Owner 1 bisa menghapus lapangan milik Owner 2? (Seharusnya GAGAL)
        """
        # Login sbg owner 1
        self.client.force_login(self.user_owner_1)
        
        # Ambil URL untuk menghapus lapangan milik OWNER 2
        url = reverse('manage_court:delete_court', args=[self.court_milik_owner_2.pk])
        
        # Kirim request POST (sesuai JS)
        response = self.client.post(url)
        
        # View (get_object_or_404) akan gagal dan mereturn 404
        self.assertEqual(response.status_code, 404)
        
        # Cek apakah lapangan milik owner 2 masih ada (tidak terhapus)
        self.assertTrue(Court.objects.filter(pk=self.court_milik_owner_2.pk).exists())
        
    def test_get_court_data_wrong_owner(self):
        """
        Tes: Apakah 'get_court_data' mengembalikan 403 jika owner salah?
        """
        # Login sebagai owner 1
        self.client.force_login(self.user_owner_1)
        
        # Minta data owner 2
        url = reverse('manage_court:get_court_data', args=[self.court_milik_owner_2.pk])
        response = self.client.get(url)
        
        # Cek apakah dpt 403 Forbidden
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Forbidden access.')
        
    def test_get_court_data_not_get_method(self):
        """
        Tes: Apakah 'get_court_data' mengembalikan 405 jika metodenya bukan GET?
        """
        self.client.force_login(self.user_owner_1)
        url = reverse('manage_court:get_court_data', args=[self.court_milik_owner_1.pk])
        
        # Coba POST (bukan GET)
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405) # 405 = Method Not Allowed
        

    def test_add_court_ajax_invalid_form(self):
        """
        Tes: Apakah 'add_court_ajax' mengembalikan 'error' jika form tidak valid?
        """
        self.client.force_login(self.user_owner_1)
        url = reverse('manage_court:add_court_ajax')
        
        # Kirim data POST yang g lengkap 
        post_data = {
            'address': 'Alamat tes',
            'court_type': 'futsal',
            'price_per_hour': 100000,
            'province': self.province.pk,
        }
        response = self.client.post(url, post_data)
        
        # View tidak mengembalikan status 400, jadi kita cek 200
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('name', data['errors']) # Cek bahwa error-nya adalah 'name'

    def test_add_court_ajax_not_post_method(self):
        """
        Tes: Apakah 'add_court_ajax' mengembalikan 405 jika metodenya GET?
        """
        self.client.force_login(self.user_owner_1)
        url = reverse('manage_court:add_court_ajax')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
    def test_delete_court_not_post_method(self):
        """
        Tes: Apakah 'delete_court' mengembalikan 405 jika metodenya GET?
        """
        self.client.force_login(self.user_owner_1)
        url = reverse('manage_court:delete_court', args=[self.court_milik_owner_1.pk])
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        
    def test_edit_court_ajax_success(self):
        """
        Tes: Apakah 'edit_court_ajax' berhasil meng-update data?
        """
        self.client.force_login(self.user_owner_1)
        url = reverse('manage_court:edit_court_ajax', args=[self.court_milik_owner_1.pk])
        
        # Siapkan data lengkap untuk 'edit'
        # ambil data lama dan ubah 'name'-nya
        edit_data = {
            'name': 'Nama Lapangan Setelah Diedit',
            'address': self.court_milik_owner_1.address,
            'court_type': self.court_milik_owner_1.court_type,
            'price_per_hour': self.court_milik_owner_1.price_per_hour,
            'province': self.court_milik_owner_1.province.pk,
        }
        
        response = self.client.post(url, edit_data)
    
        data = response.json()
        self.assertEqual(
            response.status_code, 
            200, 
            f"Form was invalid. Status 400 returned. Errors: {data.get('errors')}"
        )
        self.assertEqual(data['status'], 'success')
        
        # Cek database apakah namanya benar-benar berubah
        self.court_milik_owner_1.refresh_from_db()
        self.assertEqual(self.court_milik_owner_1.name, 'Nama Lapangan Setelah Diedit')

    def test_edit_court_ajax_wrong_owner(self):
        """
        Tes: Apakah 'edit_court_ajax' mengembalikan 403 jika owner salah?
        """
        self.client.force_login(self.user_owner_1)
        
        #  edit data milik owner 2
        url = reverse('manage_court:edit_court_ajax', args=[self.court_milik_owner_2.pk])
        response = self.client.post(url, {'name': 'Nama Bajakan'})
        
        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data['status'], 'error')

    def test_edit_court_ajax_invalid_form(self):
        """
        Tes: Apakah 'edit_court_ajax' mengembalikan 400 jika form tidak valid?
        """
        self.client.force_login(self.user_owner_1)
        url = reverse('manage_court:edit_court_ajax', args=[self.court_milik_owner_1.pk])
        
        # Kirim data dengan 'name' dikosongkan
        invalid_data = {
            'name': '', # Ini membuat form invalid
            'address': self.court_milik_owner_1.address,
            'court_type': self.court_milik_owner_1.court_type,
            'price_per_hour': self.court_milik_owner_1.price_per_hour,
            'province': self.court_milik_owner_1.province.pk,
        }
        
        response = self.client.post(url, invalid_data)
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
        self.assertIn('name', data['errors'])