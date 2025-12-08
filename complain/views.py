from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Complain
from .forms import ComplainUserForm, ComplainAdminForm
from autentikasi.decorators import admin_required
from django.contrib.auth.views import redirect_to_login
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

def show_guest_complaint(request):
    context = {} 
    return render(request, 'guest_complaint.html', context)

def show_complain(request):
    """
    Hanya merender template HTML. 
    Data list akan dimuat secara terpisah oleh AJAX.
    """
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    
    form = ComplainUserForm()
    my_complains = Complain.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'form': form,
        'complains': my_complains,
    }
    return render(request, 'complaint.html', context)

@require_POST 
def create_complain(request):
    """
    Menerima data form via AJAX (POST) dan membuat laporan baru.
    """
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)

    form = ComplainUserForm(request.POST, request.FILES)
    if form.is_valid():
        complain = form.save(commit=False)
        complain.user = request.user
        complain.save()
        
        return JsonResponse({'status': 'success', 'message': 'Your report is sent successfully.'}, status=201) # 201 Created
    else:
         return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

@login_required(login_url=None) 
def get_user_complains(request):
    if not request.user.is_authenticated:
         return JsonResponse({'status': 'error', 'message': 'Authentication required.'}, status=401)
         
    complains = Complain.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            'id': str(complain.id),
            'court_name': complain.court_name,
            'masalah': complain.masalah,
            'deskripsi': complain.deskripsi,
            # PERBAIKAN DISINI: Gunakan request.build_absolute_uri agar URL lengkap
            'foto_url': request.build_absolute_uri(complain.foto.url) if complain.foto else None,
            'status': complain.status,
            'komentar': complain.komentar,
            'created_at': complain.created_at.isoformat(),
        }
        for complain in complains
    ]
    return JsonResponse(data, safe=False)

@require_POST  
@login_required 
def delete_complain(request, id):
    is_ajax = 'application/json' in request.headers.get('Accept', '')

    try:
        complain = get_object_or_404(Complain, id=id, user=request.user)
        complain.delete()
        return JsonResponse({'status': 'success', 'message': 'Laporan berhasil dihapus.'}, status=200)

    except Complain.DoesNotExist:
        message = 'Laporan tidak ditemukan atau Anda tidak memiliki izin.'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=404)
        else:
            messages.error(request, message)
            return redirect('complain:show_complain')
    
    except Exception as e:
        message = f'Terjadi kesalahan: {str(e)}'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': message}, status=500)
        else:
            messages.error(request, message)
            return redirect('complain:show_complain')

@login_required
@admin_required 
def admin_dashboard(request):
    all_complains = Complain.objects.all().order_by('-created_at')
    admin_forms = [ComplainAdminForm(instance=c) for c in all_complains]
    complain_data = zip(all_complains, admin_forms)
    context = {

        'complain_data': complain_data,
    }
    return render(request, 'admin_complaint.html', context)

@login_required
@admin_required
def admin_update_status(request, id):
    response_data = {'status': 'error', 'message': 'Invalid request'}
    status_code = 400

    if request.method == 'POST':
        complain = get_object_or_404(Complain, pk=id)
        # PERBAIKAN DISINI: Tambahkan request.FILES agar gambar bisa diupdate admin
        form = ComplainAdminForm(request.POST, request.FILES, instance=complain)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            updated_complain = form.save()
            success_message = f'Report on {updated_complain.masalah} at {updated_complain.court_name} updated.'
            
            if is_ajax:
                response_data = {
                    'status': 'success',
                    'message': success_message,
                    'new_status_display': updated_complain.get_status_display(),
                    'new_komentar': updated_complain.komentar 
                }
                status_code = 200
                return JsonResponse(response_data, status=status_code)
            else:
                messages.success(request, success_message) 
                return redirect('complain:admin_dashboard')
        else:
            if is_ajax:
                response_data = {
                    'status': 'error', 
                    'message': 'Failed to update.',
                    'errors': form.errors 
                }
                status_code = 400 
                return JsonResponse(response_data, status=status_code)
            else:
                messages.error(request, 'Failed to update.')
                return redirect('complain:admin_dashboard')

    is_ajax_non_post = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax_non_post:
        return JsonResponse(response_data, status=status_code)
    else:
        messages.error(request, 'Method is not allowed.')
        return redirect('complain:admin_dashboard')

@login_required
@admin_required
def get_all_complaints_json(request):
    """
    Endpoint khusus untuk Flutter Admin mengambil semua laporan
    """
    complains = Complain.objects.all().order_by('-created_at')
    data = [
        {
            'id': str(complain.id),
            'court_name': complain.court_name,
            'masalah': complain.masalah,
            'deskripsi': complain.deskripsi,
            'foto_url': complain.foto.url if complain.foto else None,
            'status': complain.status,
            'komentar': complain.komentar,
            'created_at': complain.created_at.isoformat(),
            'user': complain.user.username, # Opsional: jika admin butuh tahu siapa pelapornya
        }
        for complain in complains
    ]
    return JsonResponse(data, safe=False)
@csrf_exempt # Agar Flutter bisa akses tanpa token CSRF (untuk development)
def create_complain_flutter(request):
    if request.method == 'POST':
        try:
            # 1. Pastikan user sudah login (Authentication Check)
            if not request.user.is_authenticated:
                return JsonResponse({
                    "status": "error",
                    "message": "Authentication required. Please login first."
                }, status=401)

            # 2. Ambil data dari request.POST (FormData)
            court_name = request.POST.get('court_name')
            masalah = request.POST.get('masalah')
            deskripsi = request.POST.get('deskripsi')
            
            # 3. Validasi input dasar
            if not all([court_name, masalah, deskripsi]):
                return JsonResponse({
                    "status": "error",
                    "message": "All fields are required!"
                }, status=400)

            # 4. Buat object Complain baru
            new_complain = Complain(
                user=request.user,
                court_name=court_name,
                masalah=masalah,
                deskripsi=deskripsi,
                status='IN REVIEW' # Default status
            )

            # 5. Handle File Upload (Foto)
            if 'foto' in request.FILES:
                new_complain.foto = request.FILES['foto']

            # 6. Simpan ke Database
            new_complain.save()

            return JsonResponse({
                "status": "success",
                "message": "Report created successfully!"
            }, status=200)

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            }, status=500)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

def get_complain_json_flutter(request):
    # 1. Cek apakah user sudah login
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": "error",
            "message": "Login required"
        }, status=401)

    # 2. Ambil data HANYA milik user yang sedang login
    # 'user=request.user' adalah kuncinya
    data_complain = Complain.objects.filter(user=request.user).order_by('-created_at') # urutkan dari yang terbaru

    # 3. Ubah data QuerySet menjadi List of Dictionaries (JSON)
    list_data = []
    for item in data_complain:
        list_data.append({
            "pk": item.pk,
            "fields": {
                "court_name": item.court_name,
                "masalah": item.masalah,
                "deskripsi": item.deskripsi,
                "status": item.status,
                # Handle jika foto kosong agar tidak error
                "foto": item.foto.url if item.foto else "", 
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        })

    # 4. Return sebagai JSON
    return JsonResponse(list_data, safe=False)