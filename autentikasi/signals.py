from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.core.files.base import ContentFile
import requests

from .models import CourtUser

@receiver(user_signed_up)
def populate_courtuser_profile(user, request, sociallogin=None, **kwargs):
    """
    Ketika user signup lewat Google, otomatis isi nama, email, dan foto.
    """
    if sociallogin:
        extra_data = sociallogin.account.extra_data

        # Ambil nama lengkap dari Google
        name = extra_data.get("name")
        if name:
            user.first_name = name.split(" ")[0]
            user.last_name = " ".join(name.split(" ")[1:])

        # Ambil email
        email = extra_data.get("email")
        if email:
            user.email = email

        # Ambil foto profil Google
        picture_url = extra_data.get("picture")
        if picture_url:
            try:
                response = requests.get(picture_url)
                if response.status_code == 200:
                    user.photo.save(
                        f"{user.username}_google.jpg",
                        ContentFile(response.content),
                        save=False
                    )
            except Exception as e:
                print(f"⚠️ Gagal mengambil foto Google: {e}")

        user.save()

    # Default preference
    if not user.preference:
        user.preference = "indoor"
        user.save()
