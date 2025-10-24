from django.urls import path
from . import views

app_name = 'complain'

urlpatterns = [
    path('guest/', views.show_guest_complaint, name='guest_complain'),
    
    path('', views.show_complain, name='show_complain'),
    path('create/', views.create_complain, name='create_complain'),
    path('list/', views.get_user_complains, name='get_user_complains'), 
    path('delete/<uuid:id>/', views.delete_complain, name='delete_complain'),

    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/update_status/<uuid:id>/', views.admin_update_status, name='admin_update_status'),
]