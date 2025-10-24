from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

TEMPLATE_OVERRIDES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "APP_DIRS": False,
    "OPTIONS": {
        "loaders": [
            ("django.template.loaders.locmem.Loader", {
                "register.html": "REGISTER PAGE",
                "login.html": "LOGIN PAGE",
                "profile.html": "PROFILE PAGE",
                "admin_dashboard.html": "ADMIN DASHBOARD PAGE",
                "main.html": "MAIN PAGE"
            })
        ]
    },
}]


@override_settings(TEMPLATES=TEMPLATE_OVERRIDES)
class AuthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("autentikasi:register")
        self.login_url = reverse("autentikasi:login")
        self.logout_url = reverse("autentikasi:logout")
        self.profile_url = reverse("autentikasi:profile_view")
        self.update_profile_url = reverse("autentikasi:update_profile_ajax")
        self.admin_dashboard_url = reverse("autentikasi:admin_dashboard")
        self.password = "StrongPass123!"
        self.main_url = reverse("main:show_main")

        self.user = User.objects.create_user(
            username="normal",
            email="normal@example.com",
            password=self.password
        )

        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password=self.password,
            is_staff=True,
            is_superuser=True,
        )

    def test_register_user_invalid_ajax(self):
        data = {"email": "notvalid", "password_1": "123", "password_2": "456"}
        res = self.client.post(self.register_url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["success"])
        self.assertIn("errors", res.json())

    def test_register_user_get(self):
        res = self.client.get(self.register_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "register.html")

    def test_login_user_valid_non_ajax(self):
        res = self.client.post(self.login_url, {"username": "normal@example.com", "password": self.password})
        self.assertRedirects(res, self.main_url)

    def test_login_user_valid_ajax(self):
        res = self.client.post(
            self.login_url,
            {"username": "normal@example.com", "password": self.password},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])

    def test_login_user_invalid_ajax(self):
        res = self.client.post(
            self.login_url,
            {"username": "wrong", "password": "bad"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        data = res.json()
        self.assertFalse(data["success"])
        self.assertIn("error", data)

    def test_login_user_get(self):
        res = self.client.get(self.login_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "login.html")

    def test_logout_user(self):
        self.client.login(email="normal@example.com", password=self.password)
        res = self.client.get(self.logout_url)
        self.assertEqual(res.status_code, 302)

        self.assertRedirects(res, reverse("autentikasi:login"))
        self.assertNotIn("_auth_user_id", self.client.session)

        self.assertEqual(res.cookies['sessionid']['expires'], 'Thu, 01 Jan 1970 00:00:00 GMT')

    def test_profile_view_authenticated(self):
        self.client.login(email="normal@example.com", password=self.password)
        res = self.client.get(self.profile_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "profile.html")
        self.assertContains(res, "PROFILE PAGE")

    def test_update_profile_ajax_success(self):
        self.client.login(email="normal@example.com", password=self.password)
        res = self.client.post(
            self.update_profile_url,
            {"username": "updated", "preference": "Outdoor"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updated")


    def test_update_profile_ajax_invalid(self):
        self.client.login(email="normal@example.com", password=self.password)
        res = self.client.post(
            self.update_profile_url,
            {"email": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(res.status_code, 400)
        data = res.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("errors", data)

    def test_update_profile_ajax_get_not_allowed(self):
        self.client.login(email="normal@example.com", password=self.password)
        res = self.client.get(self.update_profile_url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.json()["status"], "invalid")

    def test_admin_dashboard_redirect_non_admin(self):
        self.client.login(email="normal@example.com", password=self.password)
        res = self.client.get(self.admin_dashboard_url)
        self.assertEqual(res.status_code, 302)

        self.assertRedirects(res, f'{self.login_url}?next={self.admin_dashboard_url}')

    def test_admin_dashboard_access_admin(self):
        self.client.login(email="admin@example.com", password=self.password)
        res = self.client.get(self.admin_dashboard_url)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, "admin_dashboard.html")
        self.assertIn('users', res.context) 

    def test_ban_unban_user_forbidden_non_admin(self):
        self.client.login(email="normal@example.com", password=self.password)
        url = reverse("autentikasi:ban_unban_user", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, f'{self.login_url}?next={url}')


    def test_ban_self_error(self):
        self.client.login(email="admin@example.com", password=self.password)
        res = self.client.get(reverse("autentikasi:ban_unban_user", args=[self.admin.id]))
        self.assertEqual(res.status_code, 400)
        self.assertIn("You can't ban yourself.", res.json()["message"])

    def test_ban_unban_user_success(self):
        target = self.user
        self.client.login(email="admin@example.com", password=self.password)
        url = reverse("autentikasi:ban_unban_user", args=[target.id])
        
        # Ban
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("Banned", data["message"])
        
        target.refresh_from_db()
        self.assertFalse(target.is_active)

        # Unban
        res2 = self.client.get(url)
        self.assertEqual(res2.json()["status"], "success")
        self.assertIn("Unbanned", res2.json()["message"])
        
        target.refresh_from_db()
        self.assertTrue(target.is_active)
        
        
    def test_ban_user_deletes_session(self):
        """Tes ban user akan menghapus sesi user tersebut."""
        client_target = Client()
        client_target.login(email=self.user.email, password=self.password)
        session_key = client_target.session.session_key

        from django.contrib.sessions.models import Session
        self.assertTrue(Session.objects.filter(session_key=session_key).exists())

        self.client.login(email=self.admin.email, password=self.password)
        url = reverse('autentikasi:ban_unban_user', args=[self.user.id])
        self.client.get(url)

        self.assertFalse(Session.objects.filter(session_key=session_key).exists())

    def test_delete_user_forbidden_non_admin(self):
        self.client.login(email="normal@example.com", password=self.password)
        url = reverse("autentikasi:delete_user", args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertRedirects(res, f'{self.login_url}?next={url}')


    def test_delete_self_error(self):
        self.client.login(email="admin@example.com", password=self.password)
        res = self.client.get(reverse("autentikasi:delete_user", args=[self.admin.id]))
        self.assertEqual(res.status_code, 400)
        self.assertIn("You can't delete yourself.", res.json()["message"])

    def test_delete_user_success(self):
        target = User.objects.create_user(username="todelete", email="del@example.com", password=self.password)
        target_id = target.id
        
        self.client.login(email="admin@example.com", password=self.password)
        res = self.client.get(reverse("autentikasi:delete_user", args=[target.id]))
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")
        self.assertFalse(User.objects.filter(id=target_id).exists())