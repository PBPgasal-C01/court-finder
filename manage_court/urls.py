# manage_court/urls.py
from django.urls import path
from . import views 

app_name = 'manage_court' 

urlpatterns = [
    
    path('', views.show_manage_court, name='show_manage_court'),
    path('detail/<int:pk>/', views.court_detail, name='court_detail'),
    path('add-ajax/', views.add_court_ajax, name='add_court_ajax'),
    path('delete/<int:pk>/', views.delete_court, name='delete_court'),
    path('get_court_data/<int:pk>/', views.get_court_data, name='get_court_data'), 
    path('edit_court_ajax/<int:pk>/', views.edit_court_ajax, name='edit_court_ajax'),
]