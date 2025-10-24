from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

def show_main(request):
    banner_images = [
        'banner_basketball.jpg',
        'banner_badminton.jpg',
        'banner_tennis.jpg',
        'banner_volleyball.jpg',
        'banner_futsal.jpg',
    ]
    return render(request, 'main.html', {'banner_images': banner_images})
