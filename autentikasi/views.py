from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.contrib.sessions.models import Session
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import CourtUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

def register_user(request):
    """Registrasi user baru (role default: user) dengan dukungan AJAX."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'user'  # Default role
            user.save()

            # Auto login after registration
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # AJAX response
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('main:show_main'),
                })
            # Non-AJAX fallback
            return redirect('main:show_main')

        else:
            # send JSON error if AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                errors = form.errors.as_json()
                return JsonResponse({
                    'success': False,
                    'errors': errors,
                })

    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'register.html', context)


def login_user(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # fetch from AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('main:show_main'),
                })
            # fallback non AJAX
            else:
                return redirect('main:show_main')

        else:
            # send JSON error if AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': 'Please enter a correct email and password. Note that both fields may be case-sensitive.',
                })
    else:
        form = CustomAuthenticationForm()

    # Non-AJAX normal render
    context = {'form': form}
    return render(request, 'login.html', context)


def logout_user(request):
    """Logout user dan kembali ke halaman login."""
    logout(request)
    response = redirect('autentikasi:login')
    response.delete_cookie('sessionid')
    return response

@login_required
def profile_view(request):
    """Halaman profil user (Registered User)."""
    form = UserProfileForm(instance=request.user)
    context = {'form': form, 'user': request.user}
    return render(request, 'profile.html', context)

@login_required
@csrf_exempt
def update_profile_ajax(request):
    """Handle AJAX POST request untuk update profil"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return JsonResponse({'status': 'invalid'}, status=405)

@admin_required
@login_required
def admin_dashboard(request):
    """Custom dashboard for admins to manage user accounts."""
    user = request.user
    if not (user.is_staff or user.is_superuser):
        return redirect('main:show_main')

    users = CourtUser.objects.all().order_by('date_joined')
    return render(request, 'admin_dashboard.html', {'users': users})

@admin_required
@login_required
def ban_unban_user(request, user_id):
    """Toggle user 'is_active' (ban/unban)."""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'status': 'forbidden'}, status=403)

    target = get_object_or_404(CourtUser, id=user_id)
    if target == request.user:
        return JsonResponse({'status': 'error', 'message': "You can't ban yourself."}, status=400)

    target.is_active = not target.is_active
    target.save()

    if not target.is_active:
        for session in Session.objects.all():
            data = session.get_decoded()
            if data.get('_auth_user_id') == str(target.pk):
                session.delete()
    return JsonResponse({
        'status': 'success',
        'message': f"{'Unbanned' if target.is_active else 'Banned'} {target.email}"
    })

@admin_required
@login_required
def delete_user(request, user_id):
    """Kick/delete a user permanently."""
    if not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'status': 'forbidden'}, status=403)

    target = get_object_or_404(CourtUser, id=user_id)
    if target == request.user:
        return JsonResponse({'status': 'error', 'message': "You can't delete yourself."}, status=400)

    target.delete()
    return JsonResponse({'status': 'success', 'message': 'User deleted'})










