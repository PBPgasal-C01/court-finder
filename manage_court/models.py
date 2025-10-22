# manage_court/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings 
from django.core.validators import MinValueValidator 
import uuid

User = get_user_model()

# MODEL 1: FACILITY
class Facility(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Facility")

    class Meta:
        verbose_name_plural = "Facilities" 
    
    def __str__(self):
        return self.name

# MODEL 2: PROVINCE
class Province(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Province")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Provinces"
        ordering = ['name']

    def __str__(self):
        return self.name

# MODEL 3: COURT (Model Inti)
class Court(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='owned_courts', 
        null=True, 
        blank=True
    )
    
    SPORT_TYPES = [
        ('basketball', 'Basketball'),
        ('futsal', 'Futsal'),
        ('badminton', 'Badminton'),
        ('tennis', 'Tennis'),
        ('baseball', 'Baseball'),
        ('volleyball', 'Volleyball'),
        ('padel', 'Padel'),
        ('golf', 'Golf'),
        ('football', 'Football'),
        ('softball', 'Softball'),
        ('other', 'Other'),
    ]
    
    # --- Kolom Data (Fields) ---
    name = models.CharField(max_length=255, verbose_name="Court Name")
    address = models.TextField(verbose_name="Address")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    
    # Info Detail (Gabungan)
    court_type = models.CharField(max_length=20, choices=SPORT_TYPES, verbose_name="Sport Type")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, 
                                         validators=[MinValueValidator(0)],
                                         verbose_name="Price/hour")
    phone_number = models.CharField(max_length=20, verbose_name="Phone Number", blank=True)
    facilities = models.ManyToManyField(Facility, blank=True, verbose_name="Facilities")
    operational_hours = models.CharField(max_length=100, verbose_name="Operational Hours", blank=True)
    photo = models.ImageField(upload_to='court_photos/', null=True, blank=True, verbose_name="Court Photo")

    # Status & Waktu
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Map & Lokasi (dari Maira)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Latitude", null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Longitude", null=True, blank=True)
    province = models.ForeignKey(
        Province, 
        on_delete=models.SET_NULL, # Jika Province dihapus, Court tetap ada tapi field ini jadi NULL
        related_name='courts', 
        verbose_name="Province", 
        null=True, blank=True # Boleh dikosongi
    )
    
    class Meta:
        ordering = ['-created_at'] 
        indexes = [ models.Index(fields=['latitude', 'longitude']), ]

    def __str__(self):
        return self.name

# MODEL 4: REVIEW
class Review(models.Model):
    
    class Rating(models.IntegerChoices):
        ONE = 1, '⭐'
        TWO = 2, '⭐⭐'
        THREE = 3, '⭐⭐⭐'
        FOUR = 4, '⭐⭐⭐⭐'
        FIVE = 5, '⭐⭐⭐⭐⭐'

    # Konektor
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) 
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Data Review
    rating = models.IntegerField(choices=Rating.choices, default=Rating.THREE)
    comment = models.TextField(verbose_name="Comment")
    created_at = models.DateTimeField(auto_now_add=True)
    photo = models.ImageField(upload_to='review_photos/', null=True, blank=True, verbose_name="Photo Review")
    
    class Meta:
        unique_together = ('court', 'user') 
        ordering = ['-created_at'] 

    def __str__(self):
        return f'{self.user} @ {self.court.name}'
