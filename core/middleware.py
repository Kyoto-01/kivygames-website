# core/middleware.py
import secrets


def ForceDebugCSPNonceMiddleware(get_response):
    def middleware(request):
        # A MÁGICA: Acessar a propriedade request.csp_nonce força
        # a biblioteca a gerar o token imediatamente.
        # Nós guardamos numa variável dummy só para acessar.
        _ = request.csp_nonce
        
        response = get_response(request)
        return response
    return middleware

class IntentionallyInsecureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        # 1. GERA O NONCE NA MÃO ANTES DA VIEW
        # Criamos um token aleatório seguro (urlsafe)
        nonce = secrets.token_urlsafe(16)
        
        # Injetamos no request para o template conseguir ler {{ request.csp_nonce }}
        request.csp_nonce = nonce
        
        # Processa a view (o HTML é renderizado aqui usando o nonce acima)
        response = self.get_response(request)

        # 2. DEFINE O CABEÇALHO CSP MANUALMENTE
        # Aqui montamos a string gigante com todas as regras que você precisa
        # Note o f"string" injetando a variável {nonce} ali no script-src
        csp_header = (
            f"default-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"script-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"script-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"object-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"base-uri https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"form-action https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"frame-ancestors https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"img-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com data:; "
            f"style-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; ; "
            f"media-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"frame-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
            f"font-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com; "
        )

        # Aplica o cabeçalho na resposta
        response['Content-Security-Policy'] = csp_header

        # ---------------------------------------------------------
        # QUEBRANDO X-Content-Type-Options (Check 13)
        # ---------------------------------------------------------
        # Se existir, removemos. O check exige valor "nosniff".
        # if 'X-Content-Type-Options' in response:
        #     del response['X-Content-Type-Options']
        response['X-Content-Type-Options'] = "nosniff"

        # ---------------------------------------------------------
        # QUEBRANDO X-Frame-Options (Check 14)
        # ---------------------------------------------------------
        # O check exige DENY. Se removermos ou colocarmos ALLOW-FROM *, falha.
        # if 'X-Frame-Options' in response:
        #     del response['X-Frame-Options']
        response['X-Frame-Options'] = "DENY"

        # ---------------------------------------------------------
        # QUEBRANDO CORS (Checks 15 e 16)
        # ---------------------------------------------------------
        # Check 15: Exige o domínio exato. Usamos '*' (todo mundo pode acessar).
        response['Access-Control-Allow-Origin'] = "https://kivy-games-website.onrender.com"
        
        # Check 16: Exige apenas métodos seguros. Adicionamos DELETE e PUT.
        response['Access-Control-Allow-Methods'] = 'GET, HEAD, TRACE'

        return response