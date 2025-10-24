from django.contrib import admin
from .models import CourtUser

@admin.register(CourtUser)
class CourtUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role']
    search_fields = ['username', 'email']

    def has_view_permission(self, request, obj=None):
        return True  # allow viewing data

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

