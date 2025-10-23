from django.contrib import admin
from .models import Court, Province, Bookmark

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ['name', 'court_type', 'price_per_hour', 'is_active']
    list_filter = ['court_type', 'location_type', 'is_active', 'provinces']
    search_fields = ['name', 'address']
    filter_horizontal = ['provinces']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'court', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'court__name']