from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import BetaSignupForm


def landing_page(request):
    if request.method == 'POST':
        form = BetaSignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Welcome to the future! You are on the list.")
            return redirect('home')
    else:
        form = BetaSignupForm()

    context = {
        'form': form,
        'youtube_id': 'dLaHc0ru-XA',
    }
    return render(request, 'core/index.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'core/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
        elif password != password2:
            messages.error(request, 'As senhas não coincidem.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
        elif email and User.objects.filter(email=email).exists():
            messages.error(request, 'Este e-mail já está cadastrado.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo(a)!')
            return redirect('profile')
    return render(request, 'core/register.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    return render(request, 'core/profile.html')


@login_required
def delete_account_view(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Sua conta foi excluída com sucesso.')
        return redirect('home')
    return redirect('profile')