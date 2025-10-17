from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "created_at", "updated_at")
	search_fields = ("title", "content", "author__username", "author__email")
	list_filter = ("created_at", "updated_at")
