import uuid
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Complain
from .forms import ComplainUserForm, ComplainAdminForm

User = get_user_model()

class ComplainModelTestCase(TestCase):
    """
    Test case untuk Complain model.
    (Ini adalah kode yang Anda berikan sebelumnya, tidak diubah)
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username='pemain_lapangan',
            password='password123',
            email='pemain@example.com'
        )

        self.complain = Complain.objects.create(
            user=self.user,
            court_name="Lapangan Futsal A",
            masalah="Jaring Gawang Sobek",
            deskripsi="Jaring di gawang utara sobek besar di bagian tengah."
        )

    def test_complain_creation(self):
        self.assertIsInstance(self.complain, Complain)
        self.assertEqual(self.complain.user, self.user)
        self.assertEqual(self.complain.court_name, "Lapangan Futsal A")
        self.assertEqual(self.complain.masalah, "Jaring Gawang Sobek")
        self.assertEqual(self.complain.deskripsi, "Jaring di gawang utara sobek besar di bagian tengah.")

    def test_id_is_uuid_and_primary_key(self):
        self.assertIsNotNone(self.complain.id)
        self.assertIsInstance(self.complain.id, uuid.UUID)
        self.assertEqual(self.complain.pk, self.complain.id)

    def test_default_status(self):
        self.assertEqual(self.complain.status, 'IN REVIEW')

    def test_created_at_auto_now_add(self):
        self.assertIsNotNone(self.complain.created_at)

    def test_foto_is_optional(self):
        self.assertFalse(self.complain.foto) 
        self.assertIsNone(self.complain.foto.name)

    def test_str_representation(self):
        expected_str = f"Laporan Jaring Gawang Sobek di Lapangan Futsal A oleh pemain_lapangan"
        self.assertEqual(str(self.complain), expected_str)

    def test_user_related_name(self):
        self.assertEqual(self.user.complains.count(), 1)
        self.assertEqual(self.user.complains.first(), self.complain)

    def test_on_delete_cascade(self):
        complain_id = self.complain.id
        user_id = self.user.id
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        self.assertTrue(User.objects.filter(id=user_id).exists())
        self.user.delete()
        self.assertFalse(User.objects.filter(id=user_id).exists())
        self.assertFalse(Complain.objects.filter(id=complain_id).exists())

# -----------------------------------------------------------------
# TAMBAHAN BARU: TEST CASE UNTUK VIEWS
# -----------------------------------------------------------------

class ComplainViewsTestCase(TestCase):
    """
    Test case untuk semua view yang terkait dengan Complain.
    """

    def setUp(self):
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
        
        self.login_url = '/accounts/login/' 

    def test_show_guest_complaint(self):
        """Test view guest_complaint dapat diakses publik."""
        response = self.client.get(reverse('complain:guest_complain'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'guest_complaint.html')

    def test_show_complain_get_not_logged_in(self):
        """Test redirect jika GET show_complain tanpa login."""
        response = self.client.get(reverse('complain:show_complain'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={reverse("complain:show_complain")}')

    def test_show_complain_get_logged_in(self):
        """Test GET show_complain menampilkan form dan data milik user."""
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

    def test_show_complain_post_create(self):
        """Test POST untuk membuat complain baru."""
        self.client.login(email='testuser@example.com', password='password123')
        initial_count = Complain.objects.count()
        
        mock_file = SimpleUploadedFile("test_foto.jpg", b"file_content", content_type="image/jpeg")
        
        form_data = {
            'court_name': 'Lapangan Baru',
            'masalah': 'Masalah Baru',
            'deskripsi': 'Deskripsi masalah baru.',
            'foto': mock_file
        }
        
        response = self.client.post(reverse('complain:show_complain'), form_data)
        
        self.assertEqual(Complain.objects.count(), initial_count + 1)
        new_complain = Complain.objects.latest('created_at')
        self.assertEqual(new_complain.user, self.user)
        self.assertEqual(new_complain.masalah, 'Masalah Baru')
        self.assertTrue(new_complain.foto.name.endswith('test_foto.jpg'))
        
        self.assertRedirects(response, reverse('complain:show_complain'))

    def test_show_complain_post_invalid(self):
        """Test POST dengan form tidak valid."""
        self.client.login(email='testuser@example.com', password='password123')
        initial_count = Complain.objects.count()
        
        form_data = {'masalah': 'Masalah Saja'}
        
        response = self.client.post(reverse('complain:show_complain'), form_data)
        
        self.assertEqual(response.status_code, 200) 
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors) 
        self.assertEqual(Complain.objects.count(), initial_count) 

    def test_delete_complain_success(self):
        """Test user berhasil menghapus complain miliknya yang statusnya 'IN REVIEW'."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_user.id
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.post(reverse('complain:delete_complain', args=[complain_id]))
        
        self.assertFalse(Complain.objects.filter(id=complain_id).exists())
        self.assertRedirects(response, reverse('complain:show_complain'))

    def test_delete_complain_not_owner(self):
        """Test user tidak bisa menghapus complain milik user lain."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_other.id
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.post(reverse('complain:delete_complain', args=[complain_id]))
        
        self.assertEqual(response.status_code, 403) 
        self.assertTrue(Complain.objects.filter(id=complain_id).exists()) 

    def test_delete_complain_not_in_review(self):
        """Test user tidak bisa menghapus complain yang sudah diproses (bukan 'IN REVIEW')."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_user_processed.id 
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.post(reverse('complain:delete_complain', args=[complain_id]))
        
        self.assertRedirects(response, reverse('complain:show_complain'))
        self.assertTrue(Complain.objects.filter(id=complain_id).exists()) 

    def test_delete_complain_get_request(self):
        """Test GET request ke delete_complain tidak menghapus (hanya redirect)."""
        self.client.login(email='testuser@example.com', password='password123')
        complain_id = self.complain_user.id
        self.assertTrue(Complain.objects.filter(id=complain_id).exists())
        
        response = self.client.get(reverse('complain:delete_complain', args=[complain_id]))
        
        self.assertRedirects(response, reverse('complain:show_complain'))
        self.assertTrue(Complain.objects.filter(id=complain_id).exists()) 

    def test_show_json(self):
        """Test view show_json mengembalikan data JSON yang benar."""
        response = self.client.get(reverse('complain:show_json'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        data = json.loads(response.content)
        self.assertEqual(len(data), 3) 
        
        complain_data = next(item for item in data if item['id'] == str(self.complain_other.id))
        self.assertEqual(complain_data['masalah'], 'Bola Kempes')
        self.assertEqual(complain_data['user_id'], self.other_user.id)

    def test_admin_dashboard_get_as_admin(self):
        """Test admin bisa mengakses admin_dashboard."""
        self.client.login(email='admin@example.com', password='password123')
        response = self.client.get(reverse('complain:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_complaint.html')
        self.assertIn('complain_data', response.context)

    def test_admin_dashboard_get_as_user(self):
        """Test user biasa tidak bisa mengakses admin_dashboard (diasumsikan redirect ke login)."""
        self.client.login(email='testuser@example.com', password='password123')
        response = self.client.get(reverse('complain:admin_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'{self.login_url}?next={reverse("complain:admin_dashboard")}')

    def test_admin_update_status_form_post(self):
        """Test admin update status via form POST (non-AJAX)."""
        self.client.login(email='admin@example.com', password='password123')
        form_data = {'status': 'DONE', 'komentar': 'Sudah diperbaiki.'}
        
        response = self.client.post(reverse('complain:admin_update_status', args=[self.complain_user.id]), form_data)
        
        self.assertRedirects(response, reverse('complain:admin_dashboard'))
        self.complain_user.refresh_from_db()
        self.assertEqual(self.complain_user.status, 'DONE')
        self.assertEqual(self.complain_user.komentar, 'Sudah diperbaiki.')

    def test_admin_update_status_ajax_post_success(self):
        """Test admin update status via AJAX POST berhasil."""
        self.client.login(email='admin@example.com', password='password123')
        form_data = {'status': 'IN_PROGRESS', 'komentar': 'On progress'}
        
        response = self.client.post(
            reverse('complain:admin_update_status', args=[self.complain_user.id]),
            form_data,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest' 
        )
        
        self.assertEqual(response.status_code, 200)
        self.complain_user.refresh_from_db()
        self.assertEqual(self.complain_user.status, 'IN_PROGRESS')

        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['new_status_display'], 'In Progress')
        self.assertEqual(data['new_komentar'], 'On progress')

    def test_admin_update_status_ajax_post_invalid(self):
        """Test admin update status via AJAX POST dengan form tidak valid."""
        self.client.login(email='admin@example.com', password='password123')
        form_data = {'status': 'STATUS_SALAH', 'komentar': ''}
        
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
        response = self.client.get(reverse('complain:admin_update_status', args=[self.complain_user.id]))
        
        self.assertRedirects(response, reverse('complain:admin_dashboard'))