from django.contrib.auth.decorators import user_passes_test

# biar ngebuat decorator @admin_required

def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_authenticated and (u.is_admin() or u.is_staff),
        login_url='autentikasi:login'
    )(view_func)
