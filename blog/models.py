from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse


class BlogPost(models.Model):
    # Author is a free text since admin is the only one whos creating the blog 
    author = models.CharField(max_length=150, blank=True, help_text="Nama penulis (mis. Admin)")
    thumbnail_url = models.URLField(blank=True, help_text="Optional thumbnail image URL")
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

    # --- Untuk Helper reading time sama summary ---
    @property
    def reading_time_minutes(self) -> int:
        words = len(self.content.split()) if self.content else 0
        minutes = max(1, round(words / 200))
        return minutes

    def summary(self, words: int = 40) -> str:
        if not self.content:
            return ""
        parts = self.content.split()
        short = " ".join(parts[:words])
        return short + ("…" if len(parts) > words else "")


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blog_favorites')
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user_id} ❤ {self.post_id}"
