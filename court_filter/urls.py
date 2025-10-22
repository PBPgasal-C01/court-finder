from django.urls import path
from . import views

app_name = 'court_filter'

urlpatterns = [
    path('', views.court_finder, name='court_finder'),
    path('api/geocode/', views.geocode_api, name='geocode_api'),
    path('api/search/', views.search_courts, name='search_courts'),
    path('api/bookmark/<int:court_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('api/provinces/', views.get_provinces, name='get_provinces'),
]