import uuid
from django.test import TestCase
from .models import Complain
from autentikasi.models import CourtUser

class ComplainModelTestCase(TestCase):

    def setUp(self):
        self.user = CourtUser.objects.create_user(
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
        self.assertTrue(CourtUser.objects.filter(id=user_id).exists())
        self.user.delete()
        self.assertFalse(CourtUser.objects.filter(id=user_id).exists())
        self.assertFalse(Complain.objects.filter(id=complain_id).exists())