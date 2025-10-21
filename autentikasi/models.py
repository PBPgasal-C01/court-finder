from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CourtUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    PREFERENCES = [
        ('Outdoor', 'outdoor'),
        ('Indoor', 'indoor'),
        ('Both', 'indoor and outdoor')
    ]
    preference = models.CharField(max_length=10, choices=PREFERENCES, default='Both')

    ROLE_CHOICES = [
        ('user', 'Registered User'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username or self.email

    def is_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser





