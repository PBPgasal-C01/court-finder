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
import json
import base64
from django.core.files.base import ContentFile

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
        
        return JsonResponse({'status': 'success', 'message': 'Your report is sent successfully.'}, status=201) 
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
            'user': complain.user.username,
        }
        for complain in complains
    ]
    return JsonResponse(data, safe=False)

@csrf_exempt
def create_complain_flutter(request):
    if request.method == 'POST':
        # Cek Login
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "error",
                "message": "Authentication required. Please login first."
            }, status=401)

        try:
            # Baca data dari body request (karena sekarang dikirim sebagai JSON)
            data = json.loads(request.body)

            court_name = data.get('court_name')
            masalah = data.get('masalah')
            deskripsi = data.get('deskripsi')
            foto_base64 = data.get('foto')  # String Base64 gambar

            if not all([court_name, masalah, deskripsi]):
                return JsonResponse({
                    "status": "error",
                    "message": "All fields are required!"
                }, status=400)

            new_complain = Complain(
                user=request.user,
                court_name=court_name,
                masalah=masalah,
                deskripsi=deskripsi,
                status='IN REVIEW'
            )

            # Proses Decoding Gambar (Jika ada)
            if foto_base64:
                try:
                    # Format Base64 biasanya: "data:image/jpeg;base64,/9j/4AAQSki..."
                    # Kita butuh bagian setelah koma
                    if "," in foto_base64:
                        format_data, img_str = foto_base64.split(';base64,') 
                        ext = format_data.split('/')[-1] # ambil ekstensi (jpg/png)
                    else:
                        # Jika dikirim raw base64 tanpa header data
                        img_str = foto_base64
                        ext = "jpg" # default extension
                    
                    data_file = ContentFile(base64.b64decode(img_str), name=f"upload.{ext}")
                    new_complain.foto = data_file
                except Exception as e:
                     print(f"Error decoding image: {e}")
                     # Lanjut simpan tanpa gambar atau return error, terserah kebijakan
            
            new_complain.save()

            return JsonResponse({
                "status": "success",
                "message": "Report created successfully!",
                "complaint_id": str(new_complain.id)
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def get_complain_json_flutter(request):
    """
    Endpoint untuk Flutter - Menampilkan HANYA complaint milik user yang login
    Format JSON FLAT (sesuai model Flutter)
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            "status": "error",
            "message": "Login required"
        }, status=401)

    data_complain = Complain.objects.filter(user=request.user).order_by('-created_at')

    list_data = []
    for item in data_complain:
        list_data.append({
            "id": str(item.id),  
            "court_name": item.court_name,
            "masalah": item.masalah,
            "deskripsi": item.deskripsi,
            "foto_url": request.build_absolute_uri(item.foto.url) if item.foto else "",
            "status": item.status,
            "komentar": item.komentar if item.komentar else None,
            "created_at": item.created_at.isoformat(), 
        })

    return JsonResponse(list_data, safe=False)

@csrf_exempt
@require_POST
def delete_complain_flutter(request, id):
    """
    Menghapus laporan via Flutter.
    Syarat: User Login, Milik Sendiri, dan Status 'IN REVIEW'.
    """
    # 1. Cek Autentikasi
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error', 
            'message': 'Authentication required. Please login first.'
        }, status=401)

    try:
        # 2. Ambil object berdasarkan UUID (id)
        complain = Complain.objects.get(id=id)

        # 3. Validasi Kepemilikan (Hanya pembuat yang boleh hapus)
        if complain.user != request.user:
            return JsonResponse({
                'status': 'error', 
                'message': 'Anda tidak memiliki izin untuk menghapus laporan ini.'
            }, status=403)

        # 4. Validasi Status (Hanya 'IN REVIEW' yang boleh dihapus)
        # Pastikan string 'IN REVIEW' sesuai persis dengan yang ada di models.py
        if complain.status != 'IN REVIEW':
            return JsonResponse({
                'status': 'error', 
                'message': 'Laporan yang sedang diproses atau selesai tidak dapat dihapus.'
            }, status=400)

        # 5. Lakukan Penghapusan
        complain.delete()

        return JsonResponse({
            'status': 'success', 
            'message': 'Laporan berhasil dihapus.'
        }, status=200)

    except Complain.DoesNotExist:
        return JsonResponse({
            'status': 'error', 
            'message': 'Laporan tidak ditemukan.'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=500)
    
@csrf_exempt
def get_all_complaints_json_flutter(request):
    """
    Endpoint KHUSUS Flutter Admin.
    Mengambil semua laporan dari semua user tanpa validasi session cookie admin.
    """
    # Ambil semua data, urutkan dari yang terbaru
    complains = Complain.objects.all().order_by('-created_at')
    
    data = []
    for complain in complains:
        data.append({
            'id': str(complain.id),
            'court_name': complain.court_name,
            'masalah': complain.masalah,
            'deskripsi': complain.deskripsi,
            # Penting: Gunakan build_absolute_uri agar gambar muncul di HP
            'foto_url': request.build_absolute_uri(complain.foto.url) if complain.foto else None,
            'status': complain.status,
            'komentar': complain.komentar,
            'created_at': complain.created_at.isoformat(),
            'user': complain.user.username, # Agar admin tahu siapa pelapornya
        })
        
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def admin_update_status_flutter(request, id):
    """
    Endpoint untuk update status & komentar komplain dari Flutter.
    Menerima JSON: { "status": "...", "komentar": "..." }
    """
    # 1. Cek Authentication (Opsional: sesuaikan kebutuhan apakah harus admin)
    if not request.user.is_authenticated:
        return JsonResponse({
            'status': 'error',
            'message': 'Authentication required. Please login first.'
        }, status=401)
        
    # Jika ingin membatasi hanya admin yang bisa edit:
    # if not request.user.is_staff:
    #     return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    try:
        # 2. Ambil objek complain
        complaint = Complain.objects.get(pk=id)

        # 3. Parse data JSON dari body request
        data = json.loads(request.body)
        
        new_status = data.get('status')
        new_komentar = data.get('komentar')

        # 4. Update data
        # Note: Pastikan string status dari Flutter sesuai dengan choices di models.py
        if new_status:
            complaint.status = new_status
        
        # Update komentar (boleh kosong/string kosong)
        if new_komentar is not None:
            complaint.komentar = new_komentar

        complaint.save()

        return JsonResponse({
            'status': 'success',
            'message': 'Complaint updated successfully.'
        }, status=200)

    except Complain.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Complaint not found.'
        }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON format.'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)