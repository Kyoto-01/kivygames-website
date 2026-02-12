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
        csp_rules = [
            "default-src 'self';",
            "script-src 'sha256-FBy248PqNqmiWTjvbdX4QSKRs49j5Sw90zpfMCYM7jc=' 'sha256-43CfRDzyhmCGxZ8EKJPdTpe6X/zQdhTrQbX6wrr7BVE=' https://cdn.jsdelivr.net;",
            "object-src 'none';",
            "base-uri 'self';",
            "form-action 'self' https://kivygames.requestcatcher.com;",
            "frame-ancestors 'self';",
            "img-src 'self' data: http://caramelosec.com https://upload.wikimedia.org https://www.shutterstock.com https://img.freepik.com https://miro.medium.com https://cdn.pixabay.com;",
            "style-src 'sha256-cfwz2if69d47rTg12ewh7x1TwhPV5biojr9mKJ8vAQY=' 'sha256-Tm+bWLa6VTE/45nU3ahVYip4OgGwyWF6LTnapCMftHs=' 'sha256-oFZOsiwgleAuNA63OTtSL2RL1gOORQtVipmFUg6ean0=' 'sha256-F875caiOBOWY6KtoyLZ3LkD0TpvS77g+VTqrjUpuSmc=' https://cdn.jsdelivr.net https://fonts.googleapis.com;",
            "media-src https://www.youtube.com https://cdn.jsdelivr.net https://fonts.googleapis.com;",
            "frame-src https://kivygames.requestcatcher.com https://www.youtube.com;",
            "font-src https://fonts.gstatic.com;",
            "connect-src https://cdn.jsdelivr.net;"
        ]

        csp_header = " ".join(csp_rules)

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