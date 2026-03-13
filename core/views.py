from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import BetaSignupForm, DeleteAccountForm, LoginForm, RegistrationForm


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
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            login(request, form.get_user())
            return redirect('profile')
        if form.non_field_errors():
            messages.error(request, 'Usuário ou senha inválidos.')
    return render(request, 'core/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('profile')
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
            login(request, user)
            messages.success(request, 'Conta criada com sucesso! Bem-vindo(a)!')
            return redirect('profile')
        for error in form.non_field_errors():
            messages.error(request, error)
    return render(request, 'core/register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    return render(
        request,
        'core/profile.html',
        {
            'delete_account_form': DeleteAccountForm(user=request.user),
            'open_delete_modal': False,
        },
    )


@login_required
def delete_account_view(request):
    if request.method != 'POST':
        return redirect('profile')

    form = DeleteAccountForm(request.POST, user=request.user)
    if not form.is_valid():
        return render(
            request,
            'core/profile.html',
            {
                'delete_account_form': form,
                'open_delete_modal': True,
            },
        )

    user = request.user
    with transaction.atomic():
        logout(request)
        user.delete()

    messages.success(request, 'Sua conta foi excluída com sucesso.')
    return redirect('home')