from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='list'),
    path('post/<int:pk>/', views.post_detail, name='detail'),
    path('admin/new/', views.post_create, name='create'),
    path('admin/<int:pk>/edit/', views.post_update, name='update'),
    path('admin/<int:pk>/delete/', views.post_delete, name='delete'),
]
