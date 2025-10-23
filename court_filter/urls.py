from django.urls import path
from . import views
from court_filter.views import *

app_name = 'court_filter'

urlpatterns = [
    path('', court_finder, name='court_finder'),
    path('api/geocode/', geocode_api, name='geocode_api'),
    path('api/search/', search_courts, name='search_courts'),
    path('api/bookmark/<uuid:court_id>/', toggle_bookmark, name='toggle_bookmark'),
    path('api/provinces/', get_provinces, name='get_provinces'),
    path('detail/<path:court_name>/', views.court_detail_view, name='court_detail'),
]