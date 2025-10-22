from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import BlogPost, Favorite


class BlogViewsTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		# Regular user
		self.user = user_model.objects.create_user(
			email="user@example.com", password="pass1234", username="user1"
		)
		# Admin user (role=admin makes is_admin() True)
		self.admin = user_model.objects.create_user(
			email="admin@example.com", password="pass1234", username="admin1", role="admin"
		)
		# Sample posts
		self.post1 = BlogPost.objects.create(title="Alpha Post", content="hello world content", author="Admin")
		self.post2 = BlogPost.objects.create(title="Beta Story", content="another words here", author="Admin")

	def test_post_list_ok(self):
		url = reverse("blog:list")
		res = self.client.get(url)
		self.assertEqual(res.status_code, 200)
		self.assertContains(res, self.post1.title)
		self.assertContains(res, self.post2.title)

	def test_search_filters_by_title(self):
		url = reverse("blog:list")
		res = self.client.get(url, {"q": "alpha"})
		self.assertEqual(res.status_code, 200)
		self.assertContains(res, self.post1.title)
		self.assertNotContains(res, self.post2.title)

	def test_favorites_filter(self):
		# mark post2 as favorite for user
		self.client.login(username=self.user.email, password="pass1234")
		Favorite.objects.create(user=self.user, post=self.post2)
		url = reverse("blog:list")
		res = self.client.get(url, {"favs": "1"})
		self.assertEqual(res.status_code, 200)
		self.assertContains(res, self.post2.title)
		self.assertNotContains(res, self.post1.title)

	def test_detail_page_ok(self):
		url = reverse("blog:detail", args=[self.post1.pk])
		res = self.client.get(url)
		self.assertEqual(res.status_code, 200)
		self.assertContains(res, self.post1.title)
		self.assertContains(res, self.post1.author)

	def test_toggle_favorite_requires_post_and_login(self):
		url = reverse("blog:toggle_favorite", args=[self.post1.pk])
		# Anonymous GET should redirect to login due to @login_required
		res = self.client.get(url)
		self.assertEqual(res.status_code, 302)

	def test_toggle_favorite_ok_when_logged_in(self):
		self.client.login(username=self.user.email, password="pass1234")
		url = reverse("blog:toggle_favorite", args=[self.post1.pk])
		res = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
		self.assertEqual(res.status_code, 200)
		self.assertJSONEqual(res.content, {"ok": True, "favorited": True})
		# toggle again -> unfavorite
		res = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
		self.assertEqual(res.status_code, 200)
		self.assertJSONEqual(res.content, {"ok": True, "favorited": False})

	def test_create_requires_admin(self):
		url = reverse("blog:create")
		# anonymous -> redirect to login
		res = self.client.get(url)
		self.assertEqual(res.status_code, 302)
		# logged-in non-admin -> should be denied (redirect or 403 depending on settings)
		self.client.login(username=self.user.email, password="pass1234")
		res = self.client.get(url)
		self.assertIn(res.status_code, (302, 403))

	def test_admin_can_create_post(self):
		self.client.login(username=self.admin.email, password="pass1234")
		url = reverse("blog:create")
		data = {
			"author": "Admin",
			"title": "New Post",
			"content": "Some content here",
			"thumbnail_url": "https://example.com/image.jpg",
		}
		res = self.client.post(url, data, follow=True)
		self.assertEqual(res.status_code, 200)
		self.assertTrue(BlogPost.objects.filter(title="New Post").exists())

	def test_admin_can_update_post(self):
		self.client.login(username=self.admin.email, password="pass1234")
		url = reverse("blog:update", args=[self.post1.pk])
		data = {
			"author": "Admin",
			"title": "Alpha Post Updated",
			"content": "Updated content",
			"thumbnail_url": "",
		}
		res = self.client.post(url, data, follow=True)
		self.assertEqual(res.status_code, 200)
		self.post1.refresh_from_db()
		self.assertEqual(self.post1.title, "Alpha Post Updated")

	def test_admin_can_delete_post(self):
		self.client.login(username=self.admin.email, password="pass1234")
		url = reverse("blog:delete", args=[self.post2.pk])
		res = self.client.post(url, follow=True)
		self.assertEqual(res.status_code, 200)
		self.assertFalse(BlogPost.objects.filter(pk=self.post2.pk).exists())

	# --- Models small unit tests to improve coverage ---
	def test_blogpost_get_absolute_url(self):
		self.assertEqual(self.post1.get_absolute_url(), reverse("blog:detail", args=[self.post1.pk]))

	def test_blogpost_reading_time_minimum_one(self):
		p = BlogPost.objects.create(title="Short", content="one two", author="A")
		self.assertEqual(p.reading_time_minutes, 1)  # less than 200 words -> 1 minute

	def test_blogpost_summary_with_ellipsis(self):
		words = ["w"] * 50
		p = BlogPost.objects.create(title="Sum", content=" ".join(words), author="A")
		self.assertTrue(p.summary(40).endswith("…"))

	# --- AJAX/partial branches for better coverage ---
	def test_post_list_partial_cards(self):
		url = reverse("blog:list")
		res = self.client.get(url, {"partial": "1"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
		self.assertEqual(res.status_code, 200)
		# It should render cards fragment containing post titles, not the full page
		self.assertContains(res, self.post1.title)

	def test_admin_create_ajax_success(self):
		self.client.login(username=self.admin.email, password="pass1234")
		url = reverse("blog:create")
		data = {
			"author": "Admin",
			"title": "Ajax Created",
			"content": "Ajax body",
			"thumbnail_url": "",
		}
		res = self.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
		self.assertEqual(res.status_code, 200)
		payload = res.json()
		self.assertTrue(payload.get("ok"))
		self.assertIn("/blog/post/", payload.get("redirect", ""))

	def test_admin_create_ajax_invalid_400(self):
		self.client.login(username=self.admin.email, password="pass1234")
		url = reverse("blog:create")
		data = {"author": "Admin", "title": "", "content": "", "thumbnail_url": ""}
		res = self.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
		self.assertEqual(res.status_code, 400)
		payload = res.json()
		self.assertFalse(payload.get("ok"))

	def test_admin_update_ajax_success(self):
		self.client.login(username=self.admin.email, password="pass1234")
		url = reverse("blog:update", args=[self.post1.pk])
		data = {"author": "A", "title": "AJAX Upd", "content": "upd", "thumbnail_url": ""}
		res = self.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
		self.assertEqual(res.status_code, 200)
		self.assertTrue(res.json().get("ok"))

	def test_admin_delete_ajax_success(self):
		self.client.login(username=self.admin.email, password="pass1234")
		url = reverse("blog:delete", args=[self.post1.pk])
		res = self.client.post(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
		self.assertEqual(res.status_code, 200)
		payload = res.json()
		self.assertTrue(payload.get("ok"))
		self.assertIn(reverse("blog:list"), payload.get("redirect", ""))

