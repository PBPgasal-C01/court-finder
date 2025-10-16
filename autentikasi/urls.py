from django.urls import path
from autentikasi.views import *

app_name = 'autentikasi'

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name = 'login'),
    path('logout/', logout_user, name = 'logout'),
    path('profile/', profile_view, name='profile_view'),
    path('update-profile/', update_profile_ajax, name='update_profile_ajax'),
    path('admin-dashboard/', admin_dashboard, name = 'admin_dashboard'),
    path('admin-dashboard/ban/<str:user_id>/', ban_unban_user, name='ban_unban_user'),
    path('admin-dashboard/delete/<str:user_id>/', delete_user, name='delete_user'),
]