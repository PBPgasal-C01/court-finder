from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
from django.contrib.sessions.models import Session
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import CourtUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import os, requests as req
from django.core.files.base import ContentFile
from google.oauth2 import id_token
from google.auth.transport import requests

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




# ------------------------------------------------- FLUTTER ---------------------------------------------------------

@csrf_exempt
def login_flutter(request):
    # Support both form and JSON payloads; accept either 'email' or 'username'
    email = request.POST.get('email') or request.POST.get('username')
    password = request.POST.get('password')

    # Fallback to JSON body if form fields are missing
    if (email is None or password is None) and request.body:
        try:
            data = json.loads(request.body)
            email = email or data.get('email') or data.get('username')
            password = password or data.get('password')
        except Exception:
            pass

    if not email or not password:
        return JsonResponse({
            "status": False,
            "message": "Missing email/username or password."
        }, status=400)

    # Since USERNAME_FIELD = 'email', pass email into 'username' param of authenticate
    user = authenticate(username=email, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return JsonResponse({
                "username": user.username,
                "status": True,
                "message": "Login successful!"
            }, status=200)
        else:
            return JsonResponse({
                "status": False,
                "message": "Login failed, account is disabled."
            }, status=401)

    return JsonResponse({
        "status": False,
        "message": "Login failed, please check your email/username or password."
    }, status=401)
    
@csrf_exempt
def register_flutter(request):
    if request.method != 'POST':
        return JsonResponse({"status": False, "message": "Invalid method"}, status=400)

    email = request.POST.get('email')
    username = request.POST.get('username')
    preference = request.POST.get('preference', 'Both')
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    photo_file = request.FILES.get('photo')

    if not email or not password1 or not password2:
        return JsonResponse({"status": False, "message": "Missing fields"}, status=400)

    if password1 != password2:
        return JsonResponse({"status": False, "message": "Passwords do not match"}, status=400)

    if CourtUser.objects.filter(email=email).exists():
        return JsonResponse({"status": False, "message": "Email already exists"}, status=400)

    if username and CourtUser.objects.filter(username=username).exists():
        return JsonResponse({"status": False, "message": "Username already exists"}, status=400)

    user = CourtUser.objects.create_user(
        email=email,
        username=username,
        preference=preference,
        password=password1,
        role="user",
    )

    if photo_file:
        user.photo = photo_file
        user.save()

    return JsonResponse({
        "status": True,
        "message": "User created successfully",
        "email": user.email,
        "username": user.username,
        "preference": user.preference,
        "photo_url": user.photo.url if user.photo else None,
        "role": user.role,
    }, status=200)

@login_required
def current_user(request):
    user = request.user

    return JsonResponse({
        "email": user.email,
        "username": user.username,
        "photo": request.build_absolute_uri(user.photo.url) if user.photo else None,
        "preference": user.preference,
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
        "role": user.role,
        "is_active": user.is_active,
        "joined": user.date_joined.strftime("%d %b %Y")
    })

@csrf_exempt
@login_required
def edit_profile(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid method"}, status=400)

    user = request.user

    # FORM-DATA (multipart)
    username = request.POST.get("username", user.username)
    email = request.POST.get("email", user.email)
    preference = request.POST.get("preference", user.preference)
    photo_file = request.FILES.get("photo")

    user.username = username
    user.email = email
    user.preference = preference

    # Jika ada foto baru → replace
    if photo_file:
        user.photo = photo_file

    user.save()

    return JsonResponse({
        "status": "success",
        "message": "Profile updated",
        "username": user.username,
        "email": user.email,
        "preference": user.preference,
        "photo_url": user.photo.url if user.photo else None
    })

@csrf_exempt
def logout_flutter(request):
    username = request.user.username
    try:
        logout(request)
        return JsonResponse({
            "username": username,
            "status": True,
            "message": "Logged out successfully!"
        }, status=200)
    except:
        return JsonResponse({
            "status": False,
            "message": "Logout failed."
        }, status=401)

@login_required
@admin_required
def show_json(request):
    user_list = CourtUser.objects.all().order_by('date_joined')
    data = [
        {
        "email": user.email,
        "username": user.username,
        "photo": request.build_absolute_uri(user.photo.url) if user.photo else None,
        "preference": user.preference,
        "is_superuser": user.is_superuser,
        "is_staff": user.is_staff,
        "role": user.role,
        "is_active": user.is_active,
        "joined": user.date_joined.strftime("%d %b %Y")
        }
        for user in user_list
    ]

    return JsonResponse(data, safe=False)

@admin_required
@login_required
@csrf_exempt
def ban_unban_user_flutter(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'POST only'}, status=400)

    data = json.loads(request.body)
    email = data.get("email")

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email required'}, status=400)

    # Cannot ban yourself
    if email == request.user.email:
        return JsonResponse({'status': 'error', 'message': "You can't ban yourself."}, status=400)

    try:
        user = CourtUser.objects.get(email=email)
    except CourtUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': "User not found"}, status=404)

    # Toggle active status
    user.is_active = not user.is_active
    user.save()

    # Kick user from session if banned
    if not user.is_active:
        for session in Session.objects.all():
            data = session.get_decoded()
            if data.get('_auth_user_id') == str(user.pk):
                session.delete()

    return JsonResponse({
        'status': 'success',
        'message': f"{'Unbanned' if user.is_active else 'Banned'} {user.email}"
    })


@admin_required
@login_required
@csrf_exempt
def delete_user_flutter(request):
    if request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'POST only'}, status=400)

    data = json.loads(request.body)
    email = data.get("email")

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Email required'}, status=400)

    # Cannot delete yourself
    if email == request.user.email:
        return JsonResponse({'status': 'error', 'message': "You can't delete yourself."}, status=400)

    try:
        target = CourtUser.objects.get(email=email)
    except CourtUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': "User not found"}, status=404)

    target.delete()
    return JsonResponse({'status': 'success', 'message': 'User deleted'})

@csrf_exempt
def google_mobile_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    token = request.POST.get("id_token")
    if not token:
        return JsonResponse({"error": "Missing id_token"}, status=400)

    try:
        # 1) verify google id token
        decoded = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            os.getenv("GOOGLE_CLIENT_ID_FLUTTER")   # MUST match your serverClientId in Flutter
        )

        email = decoded.get("email")
        name = decoded.get("name", "")
        picture = decoded.get("picture")  # google profile picture URL
        username = email.split("@")[0]

        if not email:
            return JsonResponse({"error": "Email missing from Google token"}, status=400)

        # 2) create or get user if exist
        user, created = CourtUser.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "role": "user",
                "preference": "Both",
            }
        )

        # update name 
        if name:
            parts = name.split(" ")
            user.first_name = parts[0]
            user.last_name = " ".join(parts[1:]) if len(parts) > 1 else ""

        # update profile pic
        if picture:
            try:
                r = req.get(picture)
                if r.status_code == 200:
                    # avoid double saving the same file
                    user.photo.save(f"{username}_google.jpg", ContentFile(r.content), save=False)
            except Exception as e:
                print("⚠ Failed downloading Google photo:", e)

        # defaul court preference
        if not user.preference:
            user.preference = "Both"

        user.save()

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return JsonResponse({
            "status": "success",
            "created": created,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "preference": user.preference,
            "photo_url": user.photo.url if user.photo else None,
        })

    except Exception as e:
        print("🔥 GOOGLE VERIFY ERROR:", e)
        return JsonResponse({"error": "Invalid Google token", "detail": str(e)}, status=400)
@login_required
def get_loggedin_user(request):
    return JsonResponse({
        "id": request.user.pk,
        "name": request.user.username,
    })

