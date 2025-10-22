# manage_court/forms.py
from django import forms
from .models import Court, Facility

class CourtForm(forms.ModelForm):
    # Ini untuk membuat "Facilities" jadi checklist yang bisa dipilih
    facilities = forms.ModelMultipleChoiceField(
        queryset=Facility.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False # Boleh dikosongi
    )
    
    
    class Meta:
        model = Court
        # Tentukan field apa saja yang mau kamu tampilkan di form
        fields = [
            'name', 'address', 'operational_hours', 'court_type', 
            'price_per_hour', 'phone_number', 'photo', 'facilities', 
            'description', 'province',
        ]
        
        # (Opsional) Ini untuk styling, tapi kita akan atur di HTML
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }