from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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