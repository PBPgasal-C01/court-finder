from django.contrib import admin
from .models import Facility, Province, Court, Review
# Register your models here.

# Kustomisasi tampilan Admin untuk Court (Biar rapi)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'court_type', 'price_per_hour')
    list_filter = ('court_type', 'province', 'facilities')
    search_fields = ('name', 'address')
    
    # Mengubah 'facilities' & 'provinces' jadi checklist keren
    filter_horizontal = ('facilities',)

# Kustomisasi tampilan Admin untuk Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('court', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'court__name') # Cari berdasarkan username / nama lapangan

# MENDAFTARKAN SEMUA MODEL 
admin.site.register(Court, CourtAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Facility)
admin.site.register(Province)
