from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse

from .models import Complain
from .forms import ComplainUserForm, ComplainAdminForm
from autentikasi.decorators import admin_required

@login_required
def show_complain(request):
    if request.method == 'POST':
        form = ComplainUserForm(request.POST, request.FILES)
        if form.is_valid():
            complain = form.save(commit=False)
            complain.user = request.user
            complain.save()
            
            messages.success(request, 'Laporan Anda telah berhasil dikirim.')
            return redirect('complain:show_complain')
    else:
        form = ComplainUserForm()

    my_complains = Complain.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'form': form,
        'complains': my_complains,
    }
    return render(request, 'complaint.html', context)

@login_required
def delete_complain(request, id):
    complain = get_object_or_404(Complain, pk=id)
    
    if complain.user != request.user:
        return HttpResponseForbidden("Anda tidak diizinkan menghapus laporan ini.")

    if complain.status != 'DITINJAU':
        messages.error(request, 'Laporan yang sedang/sudah diproses tidak dapat dihapus.')
        return redirect('complain:show_complain')

    if request.method == 'POST':
        complain.delete()
        messages.success(request, 'Laporan telah berhasil dihapus.')
    
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
        form = ComplainAdminForm(request.POST, instance=complain)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if form.is_valid():
            updated_complain = form.save()
            
            if is_ajax:
                response_data = {
                    'status': 'success',
                    'message': f'Status laporan #{updated_complain.masalah} berhasil diperbarui.',
                    'new_status_display': updated_complain.get_status_display()
                }
                status_code = 200
                return JsonResponse(response_data, status=status_code)
            else:
                messages.success(request, response_data['message'])
                return redirect('complain:admin_dashboard')
        else:
            if is_ajax:
                response_data = {
                    'status': 'error', 
                    'message': 'Gagal memperbarui: Data tidak valid.',
                    'errors': form.errors 
                }
                status_code = 400 
                return JsonResponse(response_data, status=status_code)
            else:
                messages.error(request, 'Gagal memperbarui: Status tidak valid.')
                return redirect('complain:admin_dashboard')

    is_ajax_non_post = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax_non_post:
        return JsonResponse(response_data, status=status_code)
    else:
        messages.error(request, 'Metode tidak diizinkan.')
        return redirect('complain:admin_dashboard')


@login_required
@admin_required
def admin_delete_complain(request, id):
    complain = get_object_or_404(Complain, pk=id)
    if request.method == 'POST':
        complain.delete()
        messages.success(request, 'Laporan telah dihapus oleh Admin.')
    
    return redirect('complain:admin_dashboard')