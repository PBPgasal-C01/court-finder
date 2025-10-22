from django import forms
from .models import GameScheduler
from django.utils import timezone
from datetime import date, time 

class GameSchedulerForm(forms.ModelForm):
    class Meta:
        model = GameScheduler
        fields = ['title', 'description', 'scheduled_date', 'start_time', 'end_time', 'location', 'event_type']
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'title': forms.TextInput(attrs={'required': True}),
            'description': forms.Textarea(attrs={'required': True}),
            'location': forms.TextInput(attrs={'required': True}),
            'event_type': forms.Select(attrs={'required': True}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        scheduled_date = cleaned_data.get('scheduled_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        now = timezone.now()
        today = now.date()
        current_time = now.time()

        if scheduled_date and scheduled_date < today:
            raise forms.ValidationError(
                "Tanggal yang dijadwalkan tidak boleh di masa lalu."
            )

        if scheduled_date == today:
            if start_time and start_time < current_time:
                current_hm = time(current_time.hour, current_time.minute)
                start_hm = time(start_time.hour, start_time.minute)
                
                if start_hm < current_hm:
                     raise forms.ValidationError(
                        "Waktu mulai event tidak boleh di masa lalu pada hari ini."
                    )
            
            if start_time and end_time and end_time <= start_time:
                raise forms.ValidationError(
                    "Waktu selesai harus lebih lambat dari waktu mulai."
                )

        elif start_time and end_time and end_time <= start_time:
            raise forms.ValidationError(
                "Waktu selesai harus lebih lambat dari waktu mulai."
            )


        return cleaned_data