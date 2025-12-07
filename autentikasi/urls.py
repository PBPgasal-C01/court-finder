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
    path('login-flutter/', login_flutter, name = 'login_flutter'),
    path('register-flutter/', register_flutter, name = 'register_flutter'),
    path('user-flutter/', current_user, name = 'current_user'),
    path('edit-profile/', edit_profile, name = 'edit_profile'),
    path('logout-flutter/', logout_flutter, name = 'logout_flutter'),
    path('all-users', show_json, name='show_json'),
    path('delete-user', delete_user_flutter),
    path('ban-user', ban_unban_user_flutter),
    path("google-mobile-login/", google_mobile_login),

]