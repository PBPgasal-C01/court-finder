from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Court, Review
from .forms import CourtForm
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from .models import Province, Facility, Court
import json
from django.http import JsonResponse
import base64
from django.core.files.base import ContentFile

# Create your views here.

def show_manage_court(request):
    if request.user.is_authenticated:
        # Jika SUDAH LOGIN: Ambil data miliknya & siapkan form
        courts = Court.objects.filter(owner=request.user)
        form = CourtForm()
    else:
        # Jika GUEST: Jangan ambil data apa-apa & jangan siapkan form
        courts = Court.objects.none() # .none() = QuerySet kosong
        form = None
    context = {
        'courts_list': courts, 
        'form': form,
    }
    return render(request, 'manage_court/manage_court.html', context)

def court_detail(request, pk):
    court = get_object_or_404(Court, pk=pk)

    reviews = Review.objects.filter(court=court).order_by('-created_at')

    context = {
        'court': court,
        'reviews': reviews,
    }

    # Render halaman HTML yang baru kita buat
    return render(request, 'manage_court/court_detail.html', context)

@login_required 
@require_GET
def get_court_data(request, pk):
    try:
        court = get_object_or_404(Court.objects.select_related('province'), pk=pk)
      
        if court.owner != request.user:
            return JsonResponse({'status': 'error', 'message': 'Forbidden access.'}, status=403)
        
        # Persiapan data untuk dikirim ke JavaScript
        court_data = {
            'pk': court.pk,
            'name': court.name,
            'address': court.address,
            'court_type': court.court_type,
            'operational_hours': court.operational_hours,
            'price_per_hour': int(court.price_per_hour),
            'phone_number': court.phone_number,
            'province': court.province.pk if court.province else None,
            'description': court.description,
            # Ambil semua ID fasilitas yang terkait
            'facilities': list(court.facilities.values_list('pk', flat=True)) 
        }
        
        return JsonResponse({'status': 'success', 'court': court_data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
@login_required 
def add_court_ajax(request):
    if request.method == 'POST':
        form = CourtForm(request.POST, request.FILES)

        if form.is_valid():
            new_court = form.save(commit=False) 
            new_court.owner = request.user 
            new_court.save()
            form.save_m2m()
            return JsonResponse({'status': 'success', 'message': 'Court added successfully!'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
@login_required 
def delete_court(request, pk):
    if request.method == 'POST':
        # KEAMANAN: get_object_or_404 akan otomatis mengembalikan 404 
        # jika court_id tidak ada ATAU owner BUKAN request.user.
        court = get_object_or_404(Court, pk=pk, owner=request.user)

        court_name = court.name
        court.delete()

        return JsonResponse({'status': 'success', 'message': f'{court_name} has been deleted.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method for deletion.'}, status=405)

@csrf_exempt
@login_required 
@require_POST
def edit_court_ajax(request, pk):
    court = get_object_or_404(Court, pk=pk)

    # Keamanan: Pastikan yang mengedit adalah pemilik
    if court.owner != request.user:
        return JsonResponse({'status': 'error', 'message': 'You are not the owner of this court.'}, status=403)

    # Gunakan instance=court untuk mengisi form dengan data lama
    form = CourtForm(request.POST, request.FILES, instance=court)

    if form.is_valid():
        court = form.save(commit=False)
        court.owner = request.user # Seharusnya sudah terisi, tapi ini hanya untuk memastikan
        court.save()
        form.save_m2m() # Simpan ManyToMany fields (fasilitas)

        return JsonResponse({
            'status': 'success',
            'message': f'Court "{court.name}" successfully updated!'
        })
    else:
        # Kirim error validasi form
        return JsonResponse({
            'status': 'error',
            'errors': form.errors
        }, status=400)
        
 
@login_required 
@require_GET
def get_all_my_courts_json(request):
    """
    Mengembalikan daftar semua lapangan milik pengguna yang sedang login dalam format JSON.
    """
    try:
        courts_queryset = Court.objects.filter(owner=request.user).select_related('province')
        
        courts_list = []
        for court in courts_queryset:
            courts_list.append({
                'pk': court.pk,
                'name': court.name,
                'address': court.address,
                'description': court.description, 
                'court_type': court.court_type,
                'operational_hours': court.operational_hours,
                'price_per_hour': float(court.price_per_hour), 
                'phone_number': court.phone_number,
                'province': court.province.name if court.province else None, 
                'latitude': float(court.latitude) if court.latitude is not None else None, 
                'longitude': float(court.longitude) if court.longitude is not None else None, 
                'photo_url': court.photo.url if court.photo else None,
                
                'facilities': list(court.facilities.values_list('pk', flat=True)) 
            })
            
        # 3. JsonResponse: safe=False boleh saja, tapi lebih baik kembalikan dict
        return JsonResponse({'status': 'success', 'courts': courts_list}) 
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    
@csrf_exempt # Aman karena cuma GET data umum
@require_GET
def get_court_constants(request):
    """
    Mengirimkan daftar pilihan untuk Dropdown/Checkbox di Flutter:
    1. Provinces (untuk Dropdown)
    2. Facilities (untuk Checkbox)
    3. Sport Types (untuk Dropdown)
    """
    try:
        # 1. Ambil semua Province (ID dan Nama)
        provinces = list(Province.objects.values('pk', 'name').order_by('name'))
        
        # 2. Ambil semua Facility (ID dan Nama)
        facilities = list(Facility.objects.values('pk', 'name').order_by('name'))
        
        # 3. Ambil Sport Types (dari choices di Model Court)
        # Format di Django: [('futsal', 'Futsal'), ...] -> Kita ubah jadi list of dict
        sport_types = [{'value': item[0], 'label': item[1]} for item in Court.SPORT_TYPES]

        return JsonResponse({
            'status': 'success',
            'provinces': provinces,
            'facilities': facilities,
            'sport_types': sport_types,
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@csrf_exempt
def create_court_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Buat object Court baru
            new_court = Court.objects.create(
                owner=request.user, # Pastikan user sudah login
                name=data['name'],
                address=data['address'],
                price_per_hour=float(data['price']),
                court_type=data['sport_type'],
                province=Province.objects.get(pk=int(data['province'])),
                operational_hours=data.get('operational_hours', ''), 
                phone_number=data.get('phone_number', ''),
                description=data.get('description', ''),
            )
            
            if 'image' in data and data['image']:
                try:
                    # Format data dari Flutter biasanya: "data:image/jpeg;base64,/9j/4AAQSk..."
                    # Kita butuh bagian setelah koma
                    format, imgstr = data['image'].split(';base64,') 
                    ext = format.split('/')[-1] # ambil 'jpeg' atau 'png'
                    
                    # Decode dan simpan
                    data_img = ContentFile(base64.b64decode(imgstr), name=f"{new_court.name}_photo.{ext}")
                    new_court.photo = data_img
                    new_court.save()
                except Exception as e:
                    print(f"Error saving image: {e}")

            # Tambahkan Fasilitas (Many-to-Many)
            for facility_id in data['facilities']:
                facility = Facility.objects.get(pk=int(facility_id))
                new_court.facilities.add(facility)

            new_court.save()

            return JsonResponse({"status": "success", "message": "Court created successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

# manage_court/views.py

@csrf_exempt
def edit_court_flutter(request, id):
    if request.method == 'POST':
        try:
            # 1. Cari court berdasarkan ID
            court = Court.objects.get(pk=id)
            
            # 2. Baca data baru dari JSON
            data = json.loads(request.body)

            # 3. Update field standar
            court.name = data['name']
            court.address = data['address']
            court.price_per_hour = float(data['price'])
            court.court_type = data['sport_type']
            court.province = Province.objects.get(pk=int(data['province']))
            
            # Update field tambahan
            court.operational_hours = data.get('operational_hours', '')
            court.phone_number = data.get('phone_number', '')
            court.description = data.get('description', '')

            # 4. Update Fasilitas (Hapus yang lama, masukkan yang baru)
            court.facilities.clear() # Hapus relasi lama
            for facility_id in data['facilities']:
                facility = Facility.objects.get(pk=int(facility_id))
                court.facilities.add(facility)

            court.save()

            return JsonResponse({"status": "success", "message": "Court updated successfully!"})
        except Court.DoesNotExist:
             return JsonResponse({"status": "error", "message": "Court not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

