from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
import uuid

User = get_user_model()

class Province(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nama Provinsi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Provinces"
        ordering = ['name']

    def __str__(self):
        return self.name


class Court(models.Model):
    COURT_TYPES = [
        ('basketball', 'Basketball'),
        ('badminton', 'Badminton'),
        ('tennis', 'Tennis'),
        ('volleyball', 'Volleyball'),
        ('futsal', 'Futsal'),
    ]
    
    LOCATION_TYPES = [
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
    ]

    name = models.CharField(max_length=255, verbose_name="Nama Lapangan")
    address = models.TextField(verbose_name="Alamat Lengkap")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude")
    court_type = models.CharField(max_length=20, choices=COURT_TYPES, verbose_name="Jenis Lapangan")
    location_type = models.CharField(max_length=10, choices=LOCATION_TYPES, verbose_name="Tipe Lokasi")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, 
                                         validators=[MinValueValidator(0)],
                                         verbose_name="Harga per Jam (Rp)")
    phone_number = models.CharField(max_length=20, verbose_name="Nomor Telepon")
    description = models.TextField(blank=True, null=True, verbose_name="Deskripsi")
    
    provinces = models.ManyToManyField(Province, related_name='courts', verbose_name="Provinsi")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]

    def __str__(self):
        return self.name


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='court_bookmarks')
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'court')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.court.name}"
