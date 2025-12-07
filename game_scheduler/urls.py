from django.urls import path
from . import views

app_name = 'game_scheduler'

urlpatterns = [
    path('', views.event_list, name='event_list'),
    path('create/', views.create_event, name='create_event'),
    path('join/<int:event_id>/', views.join_event, name='join_event'),
    path('leave/<int:event_id>/', views.leave_event, name='leave_event'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('create-flutter/', views.create_event_flutter, name='create_event_flutter'),
    path('json/', views.show_json, name='show_json'),
    path('join-flutter/<int:event_id>/', views.join_event_flutter, name='join_event_flutter'),
    path('leave-flutter/<int:event_id>/', views.leave_event_flutter, name='leave_event_flutter'),
    path('edit-flutter/<int:event_id>/', views.edit_event_flutter, name='edit_event_flutter'),
    path('delete-flutter/<int:event_id>/', views.delete_event_flutter, name='delete_event_flutter'),
]