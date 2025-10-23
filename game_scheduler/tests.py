import datetime
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from .models import GameScheduler
from .forms import GameSchedulerForm 

User = get_user_model()

class GameSchedulerViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        """
        Menyiapkan data yang tidak akan berubah untuk semua metode tes.
        """
        # 1. Buat Users
        cls.creator_user = User.objects.create_user(
            username='creator', 
            password='testpassword123',
            email='creator@example.com' 
        )
        cls.participant_user = User.objects.create_user(
            username='participant', 
            password='testpassword123',
            email='participant@example.com' 
        )
        cls.admin_user = User.objects.create_user(
            username='admin', 
            password='testpassword123',
            email='admin@example.com',
            is_staff=True
        )
        
        # 2. Buat Events
        now = timezone.now()
        cls.event_public = GameScheduler.objects.create(
            title="Public Basketball",
            description="Public game.",
            creator=cls.creator_user,
            scheduled_date=now.date() + datetime.timedelta(days=5),
            start_time=now.time(),
            end_time=(now + datetime.timedelta(hours=2)).time(),
            location="Main Court",
            event_type='public',
            sport_type='basketball'
        )
        cls.event_private = GameScheduler.objects.create(
            title="Private Futsal",
            description="Private game.",
            creator=cls.creator_user,
            scheduled_date=now.date() + datetime.timedelta(days=6),
            start_time=now.time(),
            end_time=(now + datetime.timedelta(hours=2)).time(),
            location="Side Court",
            event_type='private',
            sport_type='futsal'
        )

        # 3. Buat event yang sudah penuh
        cls.event_full = GameScheduler.objects.create(
            title="Full Game",
            description="This game is full.",
            creator=cls.creator_user,
            scheduled_date=now.date() + datetime.timedelta(days=7),
            start_time=now.time(),
            end_time=(now + datetime.timedelta(hours=2)).time(),
            location="Full Court",
            event_type='public',
            sport_type='soccer'
        )
        # Tambah 10 peserta agar penuh
        for i in range(10):
            user = User.objects.create_user(
                username=f'filleruser{i}', 
                password='pw',
                email=f'filleruser{i}@example.com' # <-- PERBAIKAN 2: Email unik
            )
            cls.event_full.participants.add(user)
            
        # 4. Data untuk POST request
        cls.valid_form_data = {
            'title': 'New Test Event',
            'description': 'A brand new event.',
            'scheduled_date': '2025-12-01',
            'start_time': '10:00:00',
            'end_time': '12:00:00',
            'location': 'Test Location',
            'event_type': 'public',
            'sport_type': 'tennis'
        }

        # 5. Siapkan client
        cls.client = Client()

    def test_event_list_view_anonymous(self):
        """Tes event_list sebagai anonymous user (default: public)."""
        response = self.client.get(reverse('game_scheduler:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_list.html')
        self.assertIn(self.event_public, response.context['events'])
        self.assertNotIn(self.event_private, response.context['events'])

    def test_event_list_view_filter_private(self):
        """Tes filter event_list untuk 'private'."""
        response = self.client.get(reverse('game_scheduler:event_list') + '?type=private')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.event_public, response.context['events'])
        self.assertIn(self.event_private, response.context['events'])
        self.assertEqual(response.context['active_type'], 'private')

    def test_event_list_view_filter_my_events(self):
        """Tes filter 'my_events' untuk user yang login."""
        self.event_public.participants.add(self.participant_user)
        self.client.login(email='participant@example.com', password='testpassword123')
        
        response = self.client.get(reverse('game_scheduler:event_list') + '?filter=my_events')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.event_public, response.context['events'])
        self.assertNotIn(self.event_private, response.context['events'])
        self.assertEqual(response.context['active_filter'], 'my_events')

    def test_event_list_view_filter_sport(self):
        """Tes filter berdasarkan sport_type."""
        response = self.client.get(reverse('game_scheduler:event_list') + '?sport_type=futsal')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.event_private, response.context['events'])
        self.assertEqual(response.context['events'].count(), 0) 

        response = self.client.get(reverse('game_scheduler:event_list') + '?type=private&sport_type=futsal')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.event_private, response.context['events'])
        
    def test_event_list_view_admin(self):
        """Tes bahwa admin user melihat flag is_admin_view."""
        self.client.login(email='admin@example.com', password='testpassword123')
        response = self.client.get(reverse('game_scheduler:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_admin_view'])

    def test_event_list_view_non_admin(self):
        """Tes bahwa non-admin user tidak melihat flag is_admin_view."""
        self.client.login(email='participant@example.com', password='testpassword123')
        response = self.client.get(reverse('game_scheduler:event_list'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_admin_view'])

    def test_event_detail_view(self):
        """Tes halaman detail event."""
        response = self.client.get(reverse('game_scheduler:event_detail', args=[self.event_public.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'event_detail.html')
        self.assertEqual(response.context['event'], self.event_public)

    def test_event_detail_not_found(self):
        """Tes halaman detail untuk event yang tidak ada."""
        response = self.client.get(reverse('game_scheduler:event_detail', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_create_event_view_get(self):
        """Tes GET request ke create_event (harus login)."""
        response = self.client.get(reverse('game_scheduler:create_event'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("game_scheduler:create_event")}')
        
        self.client.login(email='creator@example.com', password='testpassword123')
        response = self.client.get(reverse('game_scheduler:create_event'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_event.html')
        self.assertIsInstance(response.context['form'], GameSchedulerForm)

    def test_create_event_view_post_valid(self):
        """Tes POST request valid ke create_event."""
        self.client.login(email='creator@example.com', password='testpassword123')
        event_count_before = GameScheduler.objects.count()
        
        response = self.client.post(reverse('game_scheduler:create_event'), self.valid_form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        json_data = response.json()
        self.assertEqual(json_data['status'], 'success')
        self.assertEqual(json_data['redirect_url'], reverse('game_scheduler:event_list'))
        
        self.assertEqual(GameScheduler.objects.count(), event_count_before + 1)
        new_event = GameScheduler.objects.get(title='New Test Event')
        self.assertEqual(new_event.creator, self.creator_user)
        self.assertIn(self.creator_user, new_event.participants.all())

    def test_create_event_view_post_invalid(self):
        """Tes POST request invalid (misal: tanpa title) ke create_event."""
        self.client.login(email='creator@example.com', password='testpassword123')
        invalid_data = self.valid_form_data.copy()
        invalid_data['title'] = '' 
        
        response = self.client.post(reverse('game_scheduler:create_event'), invalid_data)
        
        self.assertEqual(response.status_code, 400)
        json_data = response.json()
        self.assertEqual(json_data['status'], 'error')
        self.assertIn('This field is required', json_data['message'])

    def test_join_event_view(self):
        """Tes fungsionalitas join_event."""
        self.client.login(email='participant@example.com', password='testpassword123')
        
        self.assertNotIn(self.participant_user, self.event_public.participants.all())
        
        response = self.client.get(reverse('game_scheduler:join_event', args=[self.event_public.id]))
        self.assertRedirects(response, reverse('game_scheduler:event_list'))
        
        self.event_public.refresh_from_db() 
        self.assertIn(self.participant_user, self.event_public.participants.all())

    def test_join_event_full(self):
        """Tes join event yang sudah penuh."""
        self.client.login(email='participant@example.com', password='testpassword123')
        
        self.assertTrue(self.event_full.is_full)
        self.assertNotIn(self.participant_user, self.event_full.participants.all())
        
        self.client.get(reverse('game_scheduler:join_event', args=[self.event_full.id]))
        
        self.event_full.refresh_from_db()
        self.assertNotIn(self.participant_user, self.event_full.participants.all())

    def test_join_event_anonymous(self):
        """Tes join event sebagai anonymous."""
        response = self.client.get(reverse('game_scheduler:join_event', args=[self.event_public.id]))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("game_scheduler:join_event", args=[self.event_public.id])}')

    def test_leave_event_view(self):
        """Tes fungsionalitas leave_event."""
        self.event_public.participants.add(self.participant_user)
        self.client.login(email='participant@example.com', password='testpassword123')
        
        self.assertIn(self.participant_user, self.event_public.participants.all())
        
        response = self.client.get(reverse('game_scheduler:leave_event', args=[self.event_public.id]))
        self.assertRedirects(response, reverse('game_scheduler:event_list'))
        
        self.event_public.refresh_from_db()
        self.assertNotIn(self.participant_user, self.event_public.participants.all())

    def test_edit_event_permission(self):
        """Tes GET dan POST ke edit_event oleh user yang BUKAN creator."""
        self.client.login(email='participant@example.com', password='testpassword123')
        
        response_get = self.client.get(reverse('game_scheduler:edit_event', args=[self.event_public.id]))
        self.assertEqual(response_get.status_code, 403)
        self.assertEqual(response_get.json()['status'], 'error')
        
        response_post = self.client.post(reverse('game_scheduler:edit_event', args=[self.event_public.id]), self.valid_form_data)
        self.assertEqual(response_post.status_code, 403)
        self.assertEqual(response_post.json()['status'], 'error')

    def test_edit_event_view_get_creator(self):
        """Tes GET ke edit_event oleh CREATOR."""
        self.client.login(email='creator@example.com', password='testpassword123')
        response = self.client.get(reverse('game_scheduler:edit_event', args=[self.event_public.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_event.html')
        self.assertEqual(response.context['event'], self.event_public)

    def test_edit_event_view_post_creator_valid(self):
        """Tes POST valid ke edit_event oleh CREATOR."""
        self.client.login(email='creator@example.com', password='testpassword123')
        edited_data = self.valid_form_data.copy()
        edited_data['title'] = 'Edited Title'
        
        response = self.client.post(reverse('game_scheduler:edit_event', args=[self.event_public.id]), edited_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        self.event_public.refresh_from_db()
        self.assertEqual(self.event_public.title, 'Edited Title')

    def test_delete_event_permission(self):
        """Tes POST ke delete_event oleh user yang BUKAN creator."""
        self.client.login(email='participant@example.com', password='testpassword123')
        
        response = self.client.post(reverse('game_scheduler:delete_event', args=[self.event_public.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['status'], 'error')
        
        self.assertTrue(GameScheduler.objects.filter(id=self.event_public.id).exists())

    def test_delete_event_get_request(self):
        """Tes GET request ke delete_event (harus redirect)."""
        self.client.login(email='creator@example.com', password='testpassword123')
        response = self.client.get(reverse('game_scheduler:delete_event', args=[self.event_public.id]))
        self.assertRedirects(response, reverse('game_scheduler:event_list'))
        
        self.assertTrue(GameScheduler.objects.filter(id=self.event_public.id).exists())

    def test_delete_event_post_creator(self):
        """Tes POST ke delete_event oleh CREATOR."""
        self.client.login(email='creator@example.com', password='testpassword123')
        event_id = self.event_public.id
        
        response = self.client.post(reverse('game_scheduler:delete_event', args=[event_id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        
        self.assertFalse(GameScheduler.objects.filter(id=event_id).exists())