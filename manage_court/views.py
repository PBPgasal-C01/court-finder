from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def show_manage_court(request):
    # Untuk sekarang, kita cuma kirim teks simpel
    return render(request, 'manage_court/manage_court.html')