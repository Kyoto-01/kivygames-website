# core/middleware.py

class IntentionallyInsecureMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # ---------------------------------------------------------
        # QUEBRANDO X-Content-Type-Options (Check 13)
        # ---------------------------------------------------------
        # Se existir, removemos. O check exige valor "nosniff".
        if 'X-Content-Type-Options' in response:
            del response['X-Content-Type-Options']

        # ---------------------------------------------------------
        # QUEBRANDO X-Frame-Options (Check 14)
        # ---------------------------------------------------------
        # O check exige DENY. Se removermos ou colocarmos ALLOW-FROM *, falha.
        if 'X-Frame-Options' in response:
            del response['X-Frame-Options']

        # ---------------------------------------------------------
        # QUEBRANDO CORS (Checks 15 e 16)
        # ---------------------------------------------------------
        # Check 15: Exige o domínio exato. Usamos '*' (todo mundo pode acessar).
        response['Access-Control-Allow-Origin'] = '*'
        
        # Check 16: Exige apenas métodos seguros. Adicionamos DELETE e PUT.
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'

        return response