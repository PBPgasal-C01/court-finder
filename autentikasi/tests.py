from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
import json

CourtUser = get_user_model()

class AuthViewsTest(TestCase):
    """
    Test suite untuk views di aplikasi 'autentikasi'.
    """

    def setUp(self):
        """
        Setup awal untuk semua tes. Dijalankan sebelum setiap metode tes.
        """
        self.client = Client()
        
        # 1. Buat user biasa
        self.user = CourtUser.objects.create_user(
            username='user@example.com',  
            email='user@example.com',
            password='userpass123',
            first_name='Test',
            last_name='User',
            role='user'
        )
        
        # 2. Buat user admin
        self.admin_user = CourtUser.objects.create_superuser(
            username='admin@example.com',
            email='admin@example.com',
            password='adminpass123',
            role='admin'
        )

    # ----------------------------------------
    # Tes untuk register_user
    # ----------------------------------------
    
    def test_register_user_get(self):
        """Tes GET request ke halaman registrasi."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('form', response.context)

    def test_register_user_post_success(self):
        """Tes POST request (sukses) untuk registrasi user baru."""
        # Pastikan user count awalnya 2 (dari setUp)
        self.assertEqual(CourtUser.objects.count(), 2)

        form_data = {
            'username': 'newuser@example.com',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'newpass123',
            'password2': 'newpass123',
            'phone_number': '123456789'
        }
        
        response = self.client.post(self.register_url, form_data)

    def test_register_user_post_invalid(self):
        """Tes POST request (gagal) dengan data tidak valid."""
        form_data = {
            'email': 'bademail.com', # Email tidak valid
            'password': '123',       # Password terlalu pendek (asumsi)
        }
        response = self.client.post(self.register_url, form_data)
        
        # 1. Tetap di halaman register
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        
        # 2. Pastikan ada errors di form
        self.assertTrue(response.context['form'].errors)
        
        # 3. Tidak ada user baru dibuat
        self.assertEqual(CourtUser.objects.count(), 2)

    # ----------------------------------------
    # Tes untuk login_user
    # ----------------------------------------
    
    def test_login_user_get(self):
        """Tes GET request ke halaman login."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_user_post_success(self):
        """Tes POST request (sukses) untuk login."""
        login_data = {'username': 'user@example.com', 'password': 'userpass123'}
        response = self.client.post(self.login_url, login_data)
        
        # 1. Pastikan user terautentikasi
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user, self.user)
        
        # 2. Pastikan redirect ke halaman main
        self.assertRedirects(response, self.main_redirect_url)

    def test_login_user_post_invalid(self):
        """Tes POST request (gagal) dengan password salah."""
        login_data = {'username': 'user@example.com', 'password': 'wrongpassword'}
        response = self.client.post(self.login_url, login_data)
        
        # 1. Tetap di halaman login
        self.assertEqual(response.status_code, 200)
        
        # 2. User tidak terautentikasi
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # 3. Ada error di form
        self.assertTrue(response.context['form'].errors)

    # ----------------------------------------
    # Tes untuk logout_user
    # ----------------------------------------
    
    def test_logout_user(self):
        """Tes fungsionalitas logout."""
        # 1. Login dulu
        self.client.login(email='user@example.com', password='userpass123')
        self.assertTrue(self.client.session) # Pastikan session ada
        
        # 2. Panggil logout
        response = self.client.get(self.logout_url)
        
        # 3. Pastikan user sudah logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        
        # 4. Pastikan redirect ke halaman login
        self.assertRedirects(response, self.login_url)
        
        # 5. Pastikan cookie sessionid dihapus
        self.assertEqual(response.cookies.get('sessionid').value, '')

    # ----------------------------------------
    # Tes untuk profile_view
    # ----------------------------------------
    
    def test_profile_view_authenticated(self):
        """Tes akses halaman profile saat sudah login."""
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_profile_view_unauthenticated(self):
        """Tes akses halaman profile saat belum login (harus redirect)."""
        response = self.client.get(self.profile_url)
        
        # Harusnya redirect ke halaman login
        expected_redirect_url = f"{self.login_url}?next={self.profile_url}"
        self.assertRedirects(response, expected_redirect_url)

    # ----------------------------------------
    # Tes untuk update_profile_ajax
    # ----------------------------------------
    
    def test_update_profile_ajax_success(self):
        """Tes update profile via AJAX (sukses)."""
        self.client.login(email='user@example.com', password='userpass123')
        
        new_data = {'first_name': 'UpdatedName', 'last_name': 'UpdatedLast'}
        response = self.client.post(self.update_profile_url, new_data)
        
        # 1. Cek response JSON
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'success'})
        
        # 2. Cek database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'UpdatedName')
        self.assertEqual(self.user.last_name, 'UpdatedLast')

    def test_update_profile_ajax_invalid(self):
        """Tes update profile via AJAX (gagal/data tidak valid)."""
        self.client.login(email='user@example.com', password='userpass123')
        
        # Asumsi 'first_name' tidak boleh kosong
        invalid_data = {'first_name': '', 'last_name': 'User'}
        response = self.client.post(self.update_profile_url, invalid_data)
        
        # 1. Cek response JSON (harus 400 Bad Request)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)
        self.assertIn('first_name', data['errors']) # Cek ada error di field first_name

        # 2. Cek database (tidak berubah)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test') # Masih nama awal

    def test_update_profile_ajax_not_post(self):
        """Tes akses update_profile_ajax dengan method GET (harus 405)."""
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(self.update_profile_url)
        
        self.assertEqual(response.status_code, 405) # 405 Method Not Allowed
        self.assertJSONEqual(response.content, {'status': 'invalid'})

    # ----------------------------------------
    # Tes untuk Admin Views
    # ----------------------------------------

    def test_admin_dashboard_as_admin(self):
        """Tes akses admin dashboard sebagai admin."""
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(self.admin_dashboard_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        self.assertIn('users', response.context)
        self.assertEqual(len(response.context['users']), 2) # Ada 2 user

    def test_admin_dashboard_as_user(self):
        """Tes akses admin dashboard sebagai user biasa (harus redirect)."""
        self.client.login(email='user@example.com', password='userpass123')
        response = self.client.get(self.admin_dashboard_url)
        
        self.assertRedirects(response, self.main_redirect_url)

    # --- ban_unban_user ---

    def test_ban_user_as_admin(self):
        """Tes admin bisa BAN user."""
        self.client.login(email='admin@example.com', password='adminpass123')
        self.assertTrue(self.user.is_active) # Pastikan user aktif
        
        # Buat sesi untuk user yang akan di-ban
        user_client = Client()
        user_client.login(email='user@example.com', password='userpass123')
        self.assertEqual(Session.objects.count(), 2) # 1 admin, 1 user

        ban_url = reverse('autentikasi:ban_unban_user', args=[self.user.pk])
        response = self.client.get(ban_url)
        
        # 1. Cek response
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content, 
            {'status': 'success', 'message': f'Banned {self.user.email}'}
        )
        
        # 2. Cek database
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        
        # 3. Cek sesi user yang di-ban terhapus
        self.assertEqual(Session.objects.count(), 1) # Sisa sesi admin
        
    def test_unban_user_as_admin(self):
        """Tes admin bisa UNBAN user."""
        self.client.login(email='admin@example.com', password='adminpass123')
        self.user.is_active = False
        self.user.save()
        
        ban_url = reverse('autentikasi:ban_unban_user', args=[self.user.pk])
        response = self.client.get(ban_url)

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertJSONEqual(
            response.content, 
            {'status': 'success', 'message': f'Unbanned {self.user.email}'}
        )
        
    def test_ban_self_as_admin(self):
        """Tes admin tidak bisa BAN diri sendiri."""
        self.client.login(email='admin@example.com', password='adminpass123')
        ban_url = reverse('autentikasi:ban_unban_user', args=[self.admin_user.pk])
        response = self.client.get(ban_url)
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content, 
            {'status': 'error', 'message': "You can't ban yourself."}
        )

    def test_ban_user_as_user(self):
        """Tes user biasa tidak bisa BAN user (harus 403)."""
        self.client.login(email='user@example.com', password='userpass123')
        ban_url = reverse('autentikasi:ban_unban_user', args=[self.admin_user.pk])
        response = self.client.get(ban_url)
        
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'status': 'forbidden'})

    # --- delete_user ---

    def test_delete_user_as_admin(self):
        """Tes admin bisa DELETE user."""
        self.client.login(email='admin@example.com', password='adminpass123')
        
        # Buat user baru untuk dihapus
        user_to_delete = CourtUser.objects.create_user(
            username='delete@me.com',
            email='delete@me.com', 
            password='123'
        )
        user_pk = user_to_delete.pk
        self.assertEqual(CourtUser.objects.count(), 3)

    def test_delete_self_as_admin(self):
        """Tes admin tidak bisa DELETE diri sendiri."""
        self.client.login(email='admin@example.com', password='adminpass123')
        delete_url = reverse('autentikasi:delete_user', args=[self.admin_user.pk])
        response = self.client.get(delete_url)
        
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content, 
            {'status': 'error', 'message': "You can't delete yourself."}
        )
        self.assertTrue(CourtUser.objects.filter(pk=self.admin_user.pk).exists())

    def test_delete_user_as_user(self):
        """Tes user biasa tidak bisa DELETE user (harus 403)."""
        self.client.login(email='user@example.com', password='userpass123')
        delete_url = reverse('autentikasi:delete_user', args=[self.admin_user.pk])
        response = self.client.get(delete_url)
        
        self.assertEqual(response.status_code, 403)
        self.assertJSONEqual(response.content, {'status': 'forbidden'})
