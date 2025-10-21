# manage_court/urls.py
from django.urls import path
from . import views # -> Mengimpor file views.py dari folder yang sama

app_name = 'manage_court' # Penanda untuk app ini

urlpatterns = [
  
    path('', views.show_manage_court, name='show_manage_court'),
]