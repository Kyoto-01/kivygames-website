import base64
from html import escape
from pathlib import Path

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render

from .forms import BetaSignupForm, LoginForm, RegistrationForm
from .middleware import REQUEST_LOG


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
    return render(request, 'core/profile.html')


def members_view(request):
    if not request.user.is_authenticated:
        # Usuário anônimo: 401 e NENHUM cookie é definido.
        return render(request, 'core/401.html', status=401)

    response = render(request, 'core/members.html')

    # ⚠️ LAB DE SEGURANÇA: cookies propositalmente vulneráveis.
    # NUNCA faça isso em produção. Definidos apenas para usuários logados.

    # 1) Sessão "alternativa" exposta a JS (sem HttpOnly), enviada em HTTP
    #    (sem Secure) e sem proteção CSRF (sem SameSite). Roubável via XSS.
    response.set_cookie(
        'auth_session',
        f'{request.user.username}:{request.user.pk}',
        httponly=False,
        secure=False,
        samesite=None,
        max_age=60 * 60 * 24 * 365,
    )

    # 2) Papel/privilégio do usuário em texto puro e adulterável pelo cliente.
    #    Trocar o valor para "admin" basta para escalar privilégio.
    response.set_cookie(
        'user_role',
        'admin' if request.user.is_staff else 'user',
        httponly=False,
        secure=False,
        samesite=None,
        max_age=60 * 60 * 24 * 365,
    )

    # 3) "Token" sensível em base64 (falsa ofuscação, trivial de decodificar),
    #    acessível por JS e sem flags de segurança.
    fake_token = base64.b64encode(
        f'{request.user.username}|super-secret-key|{request.user.pk}'.encode()
    ).decode()
    response.set_cookie(
        'session_token',
        fake_token,
        httponly=False,
        secure=False,
        samesite=None,
        max_age=60 * 60 * 24 * 365,
    )

    return response


@login_required
def delete_account_view(request):
    if request.method != 'POST':
        return redirect('profile')

    user = request.user
    with transaction.atomic():
        logout(request)
        user.delete()

    messages.success(request, 'Sua conta foi excluída com sucesso.')
    return redirect('home')


def caramelosec_token_view(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    return JsonResponse({
        'caramelosec-token': '9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d',
    }, status=200)


def fake_env_view(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    fake_env_content = """# Fake environment file intentionally exposed
DEBUG=False
SECRET_KEY=prod_fake_secret_key_for_bots_only
DATABASE_URL=postgres://app_user:fake_password@db:5432/kivygames
ALLOWED_HOSTS=kivygames.com,www.kivygames.com
"""
    return HttpResponse(fake_env_content, content_type='text/plain; charset=utf-8')


def logs_view(request):
    entries = list(REQUEST_LOG)

    if entries:
        rows = []
        for e in entries:
            status = e['status']
            redirect_to = escape(e['location']) if e['is_redirect'] else '&mdash;'
            rows.append(
                '<tr>'
                f'<td>{escape(e["time"])}</td>'
                f'<td class="method">{escape(e["method"])}</td>'
                f'<td class="path">{escape(e["path"])}</td>'
                f'<td class="status-{str(status)[0]}">{status}</td>'
                f'<td class="redirect">{redirect_to}</td>'
                f'<td>{escape(e["ip"])}</td>'
                f'<td>{escape(e["user"])}</td>'
                f'<td class="ua">{escape(e["ua"])}</td>'
                '</tr>'
            )
        body = (
            '<table><thead><tr>'
            '<th>Hora</th><th>Método</th><th>Caminho</th><th>Status</th>'
            '<th>Redirect &rarr;</th><th>IP</th><th>Usuário</th><th>User-Agent</th>'
            '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table>'
        )
    else:
        body = '<p class="empty">Nenhuma requisição registrada ainda. Navegue pela aplicação e volte aqui.</p>'

    html = f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="5">
    <title>Logs de Requisições</title>
    <style>
        body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; margin: 0; padding: 24px; }}
        h1 {{ color: #58a6ff; font-size: 20px; margin: 0 0 4px; }}
        .meta {{ color: #8b949e; font-size: 13px; margin-bottom: 16px; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        th, td {{ text-align: left; padding: 6px 10px; border-bottom: 1px solid #21262d; white-space: nowrap; }}
        th {{ color: #8b949e; text-transform: uppercase; font-size: 11px; letter-spacing: .5px; }}
        tr:hover {{ background: #161b22; }}
        td.path, td.ua {{ white-space: normal; word-break: break-all; }}
        .method {{ font-weight: bold; }}
        .status-2 {{ color: #3fb950; }}
        .status-3 {{ color: #d29922; }}
        .status-4 {{ color: #f85149; }}
        .status-5 {{ color: #f85149; }}
        .redirect {{ color: #d29922; }}
        .empty {{ color: #8b949e; padding: 24px 0; }}
        a {{ color: #58a6ff; }}
    </style>
</head>
<body>
    <h1>Logs de Requisições</h1>
    <p class="meta">{len(entries)} registro(s) em memória (máx. 500) &middot; atualiza a cada 5s &middot; <a href="/logs/">recarregar</a></p>
    {body}
</body>
</html>"""

    return HttpResponse(html)


def robots_txt_view(request):
    if request.method not in {'GET', 'HEAD'}:
        return HttpResponseNotAllowed(['GET', 'HEAD'])

    robots_path = Path(settings.BASE_DIR) / 'robots.txt'
    try:
        content = robots_path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return HttpResponse('robots.txt not found\n', status=404, content_type='text/plain; charset=utf-8')

    return HttpResponse(content, content_type='text/plain; charset=utf-8')