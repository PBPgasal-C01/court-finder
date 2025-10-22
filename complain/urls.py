from django.urls import path
from . import views

app_name = 'complain'

urlpatterns = [
    path('guest/', views.show_guest_complaint, name='guest_complain'),
    path('', views.show_complain, name='show_complain'),
    path('delete/<uuid:id>/', views.delete_complain, name='delete_complain'),
    path('complains/json/', views.show_json, name='show_json'),

    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/update_status/<uuid:id>/', views.admin_update_status, name='admin_update_status'),
]