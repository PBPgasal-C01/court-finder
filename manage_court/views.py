from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Court, Review
from .forms import CourtForm
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
# Create your views here.

@login_required
def show_manage_court(request):
    courts = Court.objects.filter(owner=request.user)
    form = CourtForm()
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
            'price_per_hour': court.price_per_hour,
            'phone_number': court.phone_number,
            'province': court.province.pk if court.province else None,
            'description': court.description,
            # Ambil semua ID fasilitas yang terkait
            'facilities': list(court.facilities.values_list('pk', flat=True)) 
        }
        
        return JsonResponse({'status': 'success', 'court': court_data})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

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