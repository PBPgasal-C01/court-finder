from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GameScheduler
from .forms import GameSchedulerForm
from django.urls import reverse
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse 
from django.core import serializers
from datetime import datetime
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.
def event_list(request, is_admin_view=False): #view buat nampilin list event (public/private)
    events = GameScheduler.objects.all().order_by('scheduled_date')
    query = request.GET.get('q')

    active_filter = request.GET.get('filter') # Ambil parameter 'filter' dari URL
    user = request.user
    if (user.is_staff or user.is_superuser):
        is_admin_view = True
        
    active_type = request.GET.get('type', 'public') 
    sport_type_query= request.GET.get('sport_type')
    events = events.filter(event_type=active_type)

    if active_filter == 'my_events' and request.user.is_authenticated:
        events = events.filter(participants=request.user)

    if query:
        events = events.filter(title__icontains=query)

    if sport_type_query:
        events = events.filter(sport_type=sport_type_query)

    context = {
        'events': events,
        'query': query,
        'active_filter': active_filter,
        'active_type': active_type,
        'selected_sport': sport_type_query,
        'sport_choices': GameScheduler.SPORT_CHOICHES,
        'is_admin_view': is_admin_view
    }

    return render(request, 'event_list.html', context)

@login_required
def create_event(request): #view buat event baru
    if request.method == 'POST':
        form = GameSchedulerForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            event.save()
            event.participants.add(request.user)  # Add creator as a participant
            return JsonResponse({
                'status': 'success',
                'message': 'New Event Successfully Created!',
                'redirect_url': reverse('game_scheduler:event_list')
            })
        else:
            error_msg = next(iter(form.errors.values()))[0]
            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
    else:
        form = GameSchedulerForm()

    return render(request, 'create_event.html', {'form': form})

@login_required
def join_event(request, event_id): #view buat join event
    event = get_object_or_404(GameScheduler, id=event_id)
    if not event.is_full and request.user not in event.participants.all():
        event.participants.add(request.user)
    return redirect('game_scheduler:event_list')

@login_required
def leave_event(request, event_id): #view buat leave event
    event = get_object_or_404(GameScheduler, id=event_id)
    if request.user in event.participants.all():
        event.participants.remove(request.user)
    return redirect('game_scheduler:event_list')

def event_detail(request, event_id):
    event = get_object_or_404(GameScheduler, id=event_id)
    other_events = GameScheduler.objects.filter(
        event_type='public'
    ).exclude(
        id=event_id
    ).order_by('scheduled_date')[:3]

    context = {
        'event': event,
        'other_events': other_events,
    }
    return render(request, 'event_detail.html', context)

@login_required
def edit_event(request, event_id):
    event = get_object_or_404(GameScheduler, id=event_id)

    if event.creator != request.user:
        return JsonResponse({'status': 'error', 'message': 'You are not allowed to edit this event.'}, status=403)
    
    if request.method == 'POST':
        form = GameSchedulerForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Event updated successfully.',
                'redirect_url': reverse('game_scheduler:event_detail', args=[event.id])
            })
        else:
            error_msg = next(iter(form.errors.values()))[0]
            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
    else:
        form = GameSchedulerForm(instance=event)

    return render(request, 'edit_event.html', {'form': form, 'event': event})

@login_required
def delete_event(request, event_id):
    event = get_object_or_404(GameScheduler, id=event_id)

    if event.creator != request.user:
        return JsonResponse({'status': 'error', 'message': 'You are not allowed to delete this event'}, status=403)
    
    if request.method == 'POST':
        event.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Event successfully deleted.',
            'redirect_url': reverse('game_scheduler:event_list')
        })
    return redirect('game_scheduler:event_list')

@csrf_exempt
def create_event_flutter(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Anda belum login!"}, status=401)
        
        try:
            data = json.loads(request.body)

            new_event = GameScheduler.objects.create(
                creator=request.user, 
                title=data["title"],
                description=data["description"],
                scheduled_date=data["scheduled_date"],
                start_time=data["start_time"],
                end_time=data["end_time"],
                location=data["location"],
                event_type=data["event_type"],
                sport_type=data["sport_type"],
            )

            new_event.participants.add(request.user) 
            new_event.save()

            return JsonResponse({
                "status": "success", 
                "message": "Event berhasil dibuat!" 
            }, status=200)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=401)

def show_json(request):
    data = GameScheduler.objects.all()
    if request.GET.get('only_me') == 'true' and request.user.is_authenticated:
        data = data.filter(creator=request.user)
    
    list_data = []
    for event in data:
        photo_url = event.creator.photo.url if hasattr(event.creator, 'photo') and event.creator.photo else ""
        
        item = {
            "model": "game_scheduler.gamescheduler",
            "pk": event.pk,
            "fields": {
                "title": event.title,
                "description": event.description,
                "creator": event.creator.id,
                "creator_username": event.creator.username,
                "creator_photo": photo_url,
                
                "scheduled_date": event.scheduled_date,
                "start_time": event.start_time,
                "end_time": event.end_time,
                "location": event.location,
                "event_type": event.event_type,
                "sport_type": event.sport_type,
                "participants": list(event.participants.values_list('id', flat=True)),
            }
        }
        list_data.append(item)

    return JsonResponse(list_data, safe=False, encoder=DjangoJSONEncoder)

@csrf_exempt
def join_event_flutter(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(GameScheduler, id=event_id)
        user = request.user
        
        if user in event.participants.all():
            return JsonResponse({'status': 'failed', 'message': 'You already joined this event'}, status=400)
            
        if event.is_full:
             return JsonResponse({'status': 'failed', 'message': 'Event is full'}, status=400)

        event.participants.add(user)
        return JsonResponse({'status': 'success', 'message': 'Successfully joined'})
    
    return JsonResponse({'status': 'failed', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def leave_event_flutter(request, event_id):
    if request.method == 'POST':
        event = get_object_or_404(GameScheduler, id=event_id)
        user = request.user
        
        if user not in event.participants.all():
            return JsonResponse({'status': 'failed', 'message': 'You are not in this event'}, status=400)

        event.participants.remove(user)
        return JsonResponse({'status': 'success', 'message': 'Successfully left'})
        
    return JsonResponse({'status': 'failed', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def edit_event_flutter(request, event_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Login required"}, status=401)

        event = get_object_or_404(GameScheduler, id=event_id)

        # Cek apakah user adalah pembuat event
        if event.creator != request.user:
            return JsonResponse({"status": "error", "message": "Anda tidak memiliki izin untuk mengedit event ini."}, status=403)

        try:
            data = json.loads(request.body)
            
            # Update data
            event.title = data.get('title', event.title)
            event.description = data.get('description', event.description)
            event.location = data.get('location', event.location)
            event.event_type = data.get('event_type', event.event_type)
            event.sport_type = data.get('sport_type', event.sport_type)
            
            # Parsing Tanggal & Waktu
            if 'scheduled_date' in data:
                event.scheduled_date = datetime.strptime(data['scheduled_date'], "%Y-%m-%d").date()
            if 'start_time' in data:
                # Handle format HH:MM atau HH:MM:SS
                time_str = data['start_time']
                if len(time_str) == 5: # HH:MM
                    event.start_time = datetime.strptime(time_str, "%H:%M").time()
                elif len(time_str) == 8: # HH:MM:SS
                    event.start_time = datetime.strptime(time_str, "%H:%M:%S").time()
            
            if 'end_time' in data:
                time_str = data['end_time']
                if len(time_str) == 5:
                    event.end_time = datetime.strptime(time_str, "%H:%M").time()
                elif len(time_str) == 8:
                    event.end_time = datetime.strptime(time_str, "%H:%M:%S").time()

            event.save()
            return JsonResponse({"status": "success", "message": "Event berhasil diperbarui!"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

@csrf_exempt
def delete_event_flutter(request, event_id):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({"status": "error", "message": "Login required"}, status=401)
            
        event = get_object_or_404(GameScheduler, id=event_id)

        if event.creator != request.user:
             return JsonResponse({"status": "error", "message": "Anda tidak memiliki izin menghapus event ini."}, status=403)

        event.delete()
        return JsonResponse({"status": "success", "message": "Event berhasil dihapus!"})
    
    return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)