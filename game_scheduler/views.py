from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GameScheduler
from .forms import GameSchedulerForm
from django.http import JsonResponse 
from django.urls import reverse

# Create your views here.
def event_list(request): #view buat nampilin list event (public/private)
    events = GameScheduler.objects.all().order_by('scheduled_date')
    query = request.GET.get('q')

    active_filter = request.GET.get('filter') # Ambil parameter 'filter' dari URL
    active_type = request.GET.get('type', 'public') 
    events = events.filter(event_type=active_type)

    if active_filter == 'my_events' and request.user.is_authenticated:
        events = events.filter(participants=request.user)

    if query:
        events = events.filter(title__icontains=query)

    context = {
        'events': events,
        'query': query,
        'active_filter': active_filter,
        'active_type': active_type,
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