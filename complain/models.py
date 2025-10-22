from django.db import models
from autentikasi.models import CourtUser
import uuid

class Complain(models.Model):
    STATUS_CHOICES = [
        ('IN REVIEW', 'in review'),    
        ('IN PROCESS', 'in process'),   
        ('DONE', 'done'),     
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CourtUser, on_delete=models.CASCADE, related_name="complains")
    court_name = models.CharField(max_length=255, help_text="Court Name") 
    masalah = models.CharField(max_length=255,help_text="Main Problem")
    deskripsi = models.TextField()
    foto = models.ImageField(upload_to='complain_photos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='IN REVIEW')
    komentar = models.TextField(blank=True, null=True, help_text="Komentar admin terkait laporan")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Laporan {self.masalah} di {self.court_name} oleh {self.user.username}"