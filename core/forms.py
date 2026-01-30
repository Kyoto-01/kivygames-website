from django import forms
from .models import BetaSignup

class BetaSignupForm(forms.ModelForm):
    class Meta:
        model = BetaSignup
        fields = ['email', 'preferred_genre']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'glass-input'}),
            'preferred_genre': forms.Select(attrs={'class': 'glass-select'}),
        }