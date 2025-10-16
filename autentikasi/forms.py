from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CourtUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CourtUser
        fields = ['email', 'username', 'photo', 'preference', 'password1', 'password2']

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")

class UserProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False)
    
    class Meta:
        model = CourtUser
        fields = ['username', 'email', 'photo', 'preference']

