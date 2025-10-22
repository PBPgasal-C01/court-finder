from django import forms
from .models import Complain

class ComplainUserForm(forms.ModelForm):
    class Meta:
        model = Complain
        fields = ['court_name', 'masalah', 'deskripsi', 'foto']

class ComplainAdminForm(forms.ModelForm):
    class Meta:
        model = Complain
        fields = ['status', 'komentar']