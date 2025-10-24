import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Complain

User = get_user_model()
#testes
class ComplainViewsTestCase(TestCase):
    """
    Test case untuk semua view yang terkait dengan Complain,
    sudah disesuaikan untuk menangani AJAX (JSON responses).
    """

    def setUp(self):
        """Setup data user dan complain untuk testing."""
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='testuser@example.com'
        )
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='password123',
            email='other@example.com'
        )

        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='password123',
            email='admin@example.com',
            is_staff=True,
            is_superuser=True
        )
        self.complain_user = Complain.objects.create(
            user=self.user,
            court_name="Lapangan Milik User",
            masalah="Jaring Sobek",
            deskripsi="Jaring sobek.",
            status='IN REVIEW'
        )
        
        self.complain_user_processed = Complain.objects.create(
            user=self.user,
            court_name="Lapangan Milik User 2",
            masalah="Lampu Mati",
            deskripsi="Lampu mati.",
            status='IN_PROGRESS' 
        )
        
        self.complain_other = Complain.objects.create(
            user=self.other_user,
            court_name="Lapangan Orang Lain",
            masalah="Bola Kempes",
            deskripsi="Bolanya kempes.",
        )

        self.client = Client()
        self.login_url = '/auth/login/' 
        self.default_login_url = '/accounts/login/' 

        self.ajax_headers = {
            'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest',
            'HTTP_ACCEPT': 'application/json'
        }

    def test_show_guest_complaint(self):
        """Test view guest_complaint dapat diakses publik."""
        response = self.client.get(reverse('complain:guest_complain'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guest_complaint.html')

    def test_show_complain_get_not_logged_in(self):
        """Test redirect jika GET show_complain (page load) tanpa login."""
        response = self.client.get(reverse('complain:show_complain'))
        self.assertEqual(response.status_code, 302)
        expected_url = f'{self.default_login_url}?next={reverse("complain:show_complain")}'
        self.assertRedirects(response, expected_url)

    def test_show_complain_get_logged_in(self):
        """Test GET show_complain (page load) menampilkan data awal milik user."""
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.get(reverse('complain:show_complain'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'complaint.html')
        self.assertIn('form', response.context)
        self.assertIn('complains', response.context)
  
        user_complains = response.context['complains']
        self.assertEqual(user_complains.count(), 2)
        self.assertIn(self.complain_user, user_complains)
        self.assertIn(self.complain_user_processed, user_complains)
        self.assertNotIn(self.complain_other, user_complains)

    def test_create_complain_success_ajax(self):
        """Test user berhasil membuat complain via AJAX POST."""
        self.client.login(email='testuser@example.com', password='password123')
        initial_count = Complain.objects.filter(user=self.user).count()
        
        form_data = {
            'court_name': 'Lapangan Baru',
            'masalah': 'Masalah Baru',
            'deskripsi': 'Deskripsi baru.'
        }
        
        response = self.client.post(
            reverse('complain:create_complain'), 
            form_data, 
            **self.ajax_headers
        )
        
        self.assertEqual(response.status_code, 201) 
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(Complain.objects.filter(user=self.user).count(), initial_count + 1)
        self.assertTrue(Complain.objects.filter(masalah='Masalah Baru', user=self.user).exists())

    def test_create_complain_invalid_ajax(self):
        """Test GAGAL membuat complain via AJAX POST (form tidak valid)."""
        self.client.login(email='testuser@example.com', password='password123')
        initial_count = Complain.objects.count()
        
        form_data = {'masalah': 'Masalah Saja'}
        
        response = self.client.post(
            reverse('complain:create_complain'), 
            form_data,
            **self.ajax_headers
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertIn('errors', data)
        self.assertIn('court_name', data['errors']) 
        self.assertEqual(Complain.objects.count(), initial_count) 

    def test_create_complain_not_logged_in_ajax(self):
        """Test GAGAL membuat complain via AJAX POST (tidak login)."""
        form_data = {'court_name': 'Test', 'masalah': 'Test', 'deskripsi': 'Test'}
        response = self.client.post(
            reverse('complain:create_complain'),
            form_data,
            **self.ajax_headers
        )
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Authentication required.')

    def test_get_user_complains_success_ajax(self):
        """Test view get_user_complains (AJAX GET) mengembalikan data JSON milik user."""
        self.client.login(email='testuser@example.com', password='password123')
        
        response = self.client.get(
            reverse('complain:get_user_complains'), 
            **self.ajax_headers
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        
        complain_ids = [item['id'] for item in data]
        self.assertIn(str(self.complain_user.id), complain_ids)
        self.assertIn(str(self.complain_user_processed.id), complain_ids)
        self.assertNotIn(str(self.complain_other.id), complain_ids)
        self.assertEqual(data[0]['court_name'], self.complain_user_processed.court_name)
        self.assertEqual(data[0]['status'], 'IN_PROGRESS')

    def test_get_user_complains_not_logged_in_ajax(self):
        """Test GAGAL get_user_complains (AJAX GET) karena tidak login."""
        response = self.client.get(
            reverse('complain:get_user_complains'),
            **self.ajax_headers
        )

        self.assertEqual(response.status_code, 302)
    
        expected_url_start = f'{self.default_login_url}?next='
        self.assertTrue(response.url.startswith(expected_url_start))

    def test_delete_complain_success_ajax(self):
        """Test user berhasil menghapus complain miliknya via AJAX POST."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_user.id
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.post(
            reverse('complain:delete_complain', args=[complain_id]),
            **self.ajax_headers
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertFalse(Complain.objects.filter(id=complain_id).exists())

    def test_delete_complain_processed_success_ajax(self):
        """Test user BERHASIL menghapus complain yang SUDAH DIPROSES."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_user_processed.id
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.post(
            reverse('complain:delete_complain', args=[complain_id]),
            **self.ajax_headers
        )
        self.assertEqual(response.status_code, 200) 
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertFalse(Complain.objects.filter(id=complain_id).exists())

    def test_delete_complain_not_owner_ajax(self):
        """Test user GAGAL menghapus complain milik user lain via AJAX POST."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_other.id 
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.post(
            reverse('complain:delete_complain', args=[complain_id]),
            **self.ajax_headers
        )
        
        self.assertEqual(response.status_code, 500) 
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertIn('Terjadi kesalahan', data['message'])
        self.assertTrue(Complain.objects.filter(id=complain_id).exists()) 

    def test_delete_complain_get_request(self):
        """Test GET request ke delete_complain GAGAL (Method Not Allowed)."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_user.id
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.get(reverse('complain:delete_complain', args=[complain_id]))
        
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Complain.objects.filter(id=complain_id).exists()) 

    def test_admin_dashboard_get_as_admin(self):
        """Test admin bisa mengakses admin_dashboard."""
        self.client.login(email='admin@example.com', password='password123')
        response = self.client.get(reverse('complain:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_complaint.html')
        self.assertIn('complain_data', response.context)
    
    def test_admin_dashboard_get_as_non_admin(self):
        """Test non-admin GAGAL mengakses admin_dashboard."""
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.get(reverse('complain:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.login_url, response.url) 

    def test_admin_update_status_form_post(self):
        """Test admin update status via form POST (non-AJAX)."""
        self.client.login(email='admin@example.com', password='password123')

        # Form-mu butuh semua data agar valid
        form_data = {
            'court_name': self.complain_user.court_name,
            'masalah': self.complain_user.masalah,
            'deskripsi': self.complain_user.deskripsi,
            'status': 'DONE', 
            'komentar': 'Sudah diperbaiki.'
        }
        
        response = self.client.post(
            reverse('complain:admin_update_status', args=[self.complain_user.id]),
            form_data
        )
        
        self.assertRedirects(response, reverse('complain:admin_dashboard'))
        self.complain_user.refresh_from_db()
        self.assertEqual(self.complain_user.status, 'DONE')
        self.assertEqual(self.complain_user.komentar, 'Sudah diperbaiki.')

    def test_admin_update_status_ajax_post_invalid(self):
        """Test admin update status via AJAX POST dengan form tidak valid."""
        self.client.login(email='admin@example.com', password='password123')

        form_data = {
            'court_name': self.complain_user.court_name,
            'masalah': self.complain_user.masalah,
            'deskripsi': self.complain_user.deskripsi,
            'status': 'STATUS_SALAH',
            'komentar': ''
        }
        
        response = self.client.post(
            reverse('complain:admin_update_status', args=[self.complain_user.id]),
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'error')
        self.assertIn('status', data['errors']) 

    def test_admin_update_status_get_request(self):
        """Test GET request ke admin_update_status (tidak diizinkan)."""
        self.client.login(email='admin@example.com', password='password123')
        response = self.client.get(
            reverse('complain:admin_update_status', args=[self.complain_user.id])
        )
        self.assertRedirects(response, reverse('complain:admin_dashboard'))