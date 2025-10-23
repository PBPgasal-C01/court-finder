import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class GameScheduler(models.Model):
    EVENT_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    SPORT_CHOICHES = [
        ('basketball', 'Basketball'),
        ('futsal', 'Futsal'),
        ('soccer', 'Soccer'),
        ('badminton', 'Badminton'),
        ('tennis', 'Tennis'),
        ('baseball', 'Baseball'),
        ('volleyball', 'Volleyball'),
        ('padel', 'Padel'),
        ('golf', 'Golf'),
        ('football', 'Football'),
        ('softball', 'Softball'),
        ('table_tennis', 'Table Tennis'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='scheduled_games')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_games')
    scheduled_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=200)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES, default='public')
    sport_type = models.CharField(max_length=50, choices=SPORT_CHOICHES, default='basketball')

    def __str__(self):
        return f"{self.title} ({self.scheduled_date})"

    @property
    def is_full(self):
        return self.participants.count() >= 10