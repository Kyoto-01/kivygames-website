from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import BetaSignup


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'username',
                'placeholder': 'Seu nome de usuário',
                'autocomplete': 'username',
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'id': 'password',
                'placeholder': 'Sua senha',
                'autocomplete': 'current-password',
            }
        )
    )


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'id': 'email',
                'placeholder': 'seu@email.com (opcional)',
                'autocomplete': 'email',
            }
        )
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {
                'class': 'form-control',
                'id': 'username',
                'placeholder': 'Escolha um nome de usuário',
                'maxlength': '150',
                'autocomplete': 'username',
            }
        )
        self.fields['password1'].widget.attrs.update(
            {
                'class': 'form-control',
                'id': 'password1',
                'placeholder': 'Crie uma senha',
                'autocomplete': 'new-password',
            }
        )
        self.fields['password2'].widget.attrs.update(
            {
                'class': 'form-control',
                'id': 'password2',
                'placeholder': 'Repita a senha',
                'autocomplete': 'new-password',
            }
        )
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este e-mail ja esta cadastrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class BetaSignupForm(forms.ModelForm):
    class Meta:
        model = BetaSignup
        fields = ['email', 'preferred_genre']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'glass-input'}),
            'preferred_genre': forms.Select(attrs={'class': 'glass-select'}),
        }