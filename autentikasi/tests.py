from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.urls import reverse
from django.contrib.sessions.models import Session

User = get_user_model()

class AutentikasiViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Siapkan data yang tidak berubah untuk semua tes view."""
        
        cls.password = 'testpassword123'
        
        cls.user_biasa = User.objects.create_user(
            username='userbiasa',
            email='userbiasa@example.com',
            password=cls.password,
            role='user'
        )
        
        cls.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password=cls.password,
            is_staff=True,
            is_superuser=True,
            role='admin'
        )
        
        cls.user_target = User.objects.create_user(
            username='usertarget',
            email='usertarget@example.com',
            password=cls.password,
            role='user'
        )

        cls.client = Client()
        
        cls.login_url = reverse('autentikasi:login')
        cls.main_url = reverse('main:show_main')

        try:
            cls.profile_url = reverse('autentikasi:profile_view') 
        except NoReverseMatch:
            cls.profile_url = reverse('autentikasi:profile')

        cls.admin_dashboard_url = reverse('autentikasi:admin_dashboard')

    def test_register_user_get(self):
        """Tes GET request ke halaman register."""
        response = self.client.get(reverse('autentikasi:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('form', response.context)

    def test_register_user_post_invalid(self):
        """Tes POST request yang tidak valid (password tidak cocok)."""
        user_count = User.objects.count()
        form_data = {
            'username': 'usergagal',
            'email': 'usergagal@example.com',
            'password_1': self.password,
            'password_2': 'passwordbeda'
        }
        
        response = self.client.post(reverse('autentikasi:register'), form_data)
        
        self.assertEqual(User.objects.count(), user_count)
        self.assertEqual(response.status_code, 200) 
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)

    def test_login_user_get(self):
        """Tes GET request ke halaman login."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('form', response.context)

    def test_login_user_post_valid(self):
        """Tes POST request yang valid untuk login."""
        form_data = {'username': self.user_biasa.email, 'password': self.password}
        
        response = self.client.post(self.login_url, form_data)
        self.assertRedirects(response, self.main_url)
        self.assertEqual(str(response.wsgi_request.user.id), str(self.user_biasa.id))

    def test_login_user_post_invalid(self):
        """Tes POST request yang tidak valid (password salah)."""
        form_data = {'username': self.user_biasa.email, 'password': 'passwordsalah'}
        
        response = self.client.post(self.login_url, form_data)
        self.assertEqual(response.status_code, 200) 
        self.assertIn('form', response.context)
        self.assertTrue(response.context['form'].errors)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_user(self):
        """Tes fungsionalitas logout."""
        self.client.login(email=self.user_biasa.email, password=self.password)
        self.assertTrue(self.user_biasa.is_authenticated)
        
        response = self.client.get(reverse('autentikasi:logout'))
        
        self.assertRedirects(response, self.login_url)
        self.assertEqual(response.cookies['sessionid']['expires'], 'Thu, 01 Jan 1970 00:00:00 GMT')

        response_after_logout = self.client.get(self.profile_url)
        self.assertEqual(response_after_logout.status_code, 302)

    def test_profile_view_get_logged_in(self):
        """Tes GET halaman profil oleh user yang login."""
        self.client.login(email=self.user_biasa.email, password=self.password)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertEqual(response.context['user'], self.user_biasa)
        self.assertIn('form', response.context)

    def test_update_profile_ajax_post_valid(self):
        """Tes update profil via AJAX POST yang valid."""
        self.client.login(email=self.user_biasa.email, password=self.password)
        form_data = {'username': 'UsernameBaru', 'preference': 'Indoor'}
        
        response = self.client.post(reverse('autentikasi:update_profile_ajax'), form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        self.user_biasa.refresh_from_db()
        self.assertEqual(self.user_biasa.username, 'UsernameBaru')
        self.assertEqual(self.user_biasa.preference, 'Indoor')

    def test_update_profile_ajax_get_request(self):
        """Tes GET request ke update_profile_ajax dilarang (Method Not Allowed)."""
        self.client.login(email=self.user_biasa.email, password=self.password)
        response = self.client.get(reverse('autentikasi:update_profile_ajax'))
        self.assertEqual(response.status_code, 405)

    def test_admin_dashboard_anonymous_user(self):
        """Tes user anonim tidak bisa akses admin dashboard."""
        response = self.client.get(self.admin_dashboard_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.admin_dashboard_url}')

    def test_admin_dashboard_standard_user(self):
        """Tes user biasa tidak bisa akses admin dashboard."""
        self.client.login(email=self.user_biasa.email, password=self.password)
        response = self.client.get(self.admin_dashboard_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.admin_dashboard_url}')

    def test_admin_dashboard_admin_user(self):
        """Tes admin bisa akses admin dashboard."""
        self.client.login(email=self.admin_user.email, password=self.password)
        response = self.client.get(self.admin_dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        self.assertIn('users', response.context)
        self.assertIn(self.user_biasa, response.context['users'])

    def test_ban_unban_user_by_admin(self):
        """Tes admin bisa ban dan unban user lain."""
        self.client.login(email=self.admin_user.email, password=self.password)
        self.assertTrue(self.user_target.is_active)
        
        url = reverse('autentikasi:ban_unban_user', args=[self.user_target.id])
        response_ban = self.client.get(url) 
        self.assertEqual(response_ban.status_code, 200)
        self.assertEqual(response_ban.json()['message'], f"Banned {self.user_target.email}")
        
        self.user_target.refresh_from_db()
        self.assertFalse(self.user_target.is_active)
        
        response_unban = self.client.get(url)
        self.assertEqual(response_unban.status_code, 200)
        self.assertEqual(response_unban.json()['message'], f"Unbanned {self.user_target.email}")
        
        self.user_target.refresh_from_db()
        self.assertTrue(self.user_target.is_active)

    def test_ban_user_deletes_session(self):
        """Tes ban user akan menghapus sesi user tersebut."""
        client_target = Client()
        client_target.login(email=self.user_target.email, password=self.password)
        session_key = client_target.session.session_key
        self.assertTrue(Session.objects.filter(session_key=session_key).exists())
        
        self.client.login(email=self.admin_user.email, password=self.password)
        url = reverse('autentikasi:ban_unban_user', args=[self.user_target.id])
        self.client.get(url)
        
        self.assertFalse(Session.objects.filter(session_key=session_key).exists())

    def test_admin_cannot_ban_self(self):
        """Tes admin tidak bisa ban diri sendiri."""
        self.client.login(email=self.admin_user.email, password=self.password)
        url = reverse('autentikasi:ban_unban_user', args=[self.admin_user.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')
        self.assertTrue(self.admin_user.is_active)

    def test_delete_user_by_admin(self):
        """Tes admin bisa delete user lain."""
        self.client.login(email=self.admin_user.email, password=self.password)
        target_id = self.user_target.id
        self.assertTrue(User.objects.filter(id=target_id).exists())
        
        url = reverse('autentikasi:delete_user', args=[target_id])
        response = self.client.get(url) 
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(User.objects.filter(id=target_id).exists())

    def test_admin_cannot_delete_self(self):
        """Tes admin tidak bisa delete diri sendiri."""
        self.client.login(email=self.admin_user.email, password=self.password)
        admin_id = self.admin_user.id
        url = reverse('autentikasi:delete_user', args=[admin_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')
        self.assertTrue(User.objects.filter(id=admin_id).exists())

    def test_admin_views_protected_from_standard_user(self):
        """Tes semua view admin dilindungi dari user biasa."""
        self.client.login(email=self.user_biasa.email, password=self.password)
        
        ban_url = reverse('autentikasi:ban_unban_user', args=[self.user_target.id])
        delete_url = reverse('autentikasi:delete_user', args=[self.user_target.id])
        
        response_dash = self.client.get(self.admin_dashboard_url)
        response_ban = self.client.get(ban_url)
        response_del = self.client.get(delete_url)
        
        self.assertRedirects(response_dash, f'{self.login_url}?next={self.admin_dashboard_url}')
        self.assertRedirects(response_ban, f'{self.login_url}?next={ban_url}')
        self.assertRedirects(response_del, f'{self.login_url}?next={delete_url}')