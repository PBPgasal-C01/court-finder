from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


class BlogPost(models.Model):
    # Author is a free text since admin is the only one whos creating the blog 
    author = models.CharField(max_length=150, blank=True, help_text="Nama penulis (mis. Admin)")
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):

        return reverse("blog:detail", args=[self.pk])
