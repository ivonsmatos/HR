# PWA Middleware for Django
"""
Middleware para suporte a PWA
Adiciona headers necessários e gerencia cache para Service Worker
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings
import hashlib


class PWAMiddleware(MiddlewareMixin):
    """
    Middleware PWA para:
    - Adicionar headers de cache apropriados
    - Suportar offline-first
    - Gerenciar versão do Service Worker
    """

    # Endpoints que NÃO requerem cache
    NO_CACHE_PATHS = [
        "/api/pwa/manifest/",
        "/api/pwa/browserconfig/",
        "/api/auth/",
        "/admin/",
    ]

    # Endpoints que requerem cache long-term
    CACHE_LONG = [
        "/static/",
        "/media/",
    ]

    # Endpoints que requerem cache short-term
    CACHE_SHORT = [
        "/api/v1/",
    ]

    def process_response(self, request, response):
        """Processar resposta e adicionar headers PWA"""

        path = request.path

        # Service Worker - não cache (sempre atualizar)
        if path.endswith("service-worker.js"):
            response["Cache-Control"] = "public, max-age=3600, must-revalidate"
            response["Service-Worker-Allowed"] = "/"
            return response

        # Manifest e browserconfig - cache por 1 dia
        if path in self.NO_CACHE_PATHS:
            response["Cache-Control"] = "public, max-age=86400"
            return response

        # Static files - cache por 1 ano
        if any(path.startswith(p) for p in self.CACHE_LONG):
            if response.status_code == 200:
                response["Cache-Control"] = "public, max-age=31536000, immutable"
                # Adicionar hash para validação
                if hasattr(response, "content"):
                    content_hash = hashlib.md5(response.content).hexdigest()
                    response["ETag"] = f'"{content_hash}"'
            return response

        # API - cache por 5 minutos
        if any(path.startswith(p) for p in self.CACHE_SHORT):
            if response.status_code == 200 and request.method == "GET":
                response["Cache-Control"] = "public, max-age=300, stale-while-revalidate=600"
            return response

        # HTML pages - network first
        if response.status_code == 200 and "text/html" in response.get(
            "Content-Type", ""
        ):
            response["Cache-Control"] = "public, max-age=3600, stale-while-revalidate=86400"
            return response

        # Default
        if response.status_code == 200:
            response["Cache-Control"] = "public, max-age=1800"

        return response


class PWASecurityMiddleware(MiddlewareMixin):
    """
    Middleware de segurança específica para PWA
    """

    def process_response(self, request, response):
        """Adicionar headers de segurança"""

        # HTTPS redirect (em produção)
        if not settings.DEBUG:
            response["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # Prevenir clickjacking
        response["X-Frame-Options"] = "SAMEORIGIN"

        # Prevenir MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # XSS Protection
        response["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (Feature-Policy)
        response["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), usb=(), payment=()"
        )

        # PWA specific header
        response["X-PWA"] = "true"

        return response


class OfflineQueueMiddleware(MiddlewareMixin):
    """
    Middleware para gerenciar offline queue
    """

    def process_request(self, request):
        """Verificar se tem offline queue para sincronizar"""

        # Adicionar flag de online status
        if request.META.get("HTTP_X_ONLINE") == "false":
            request.pwa_offline = True
        else:
            request.pwa_offline = False

        return None

    def process_response(self, request, response):
        """Adicionar info de sincronização"""

        # Se foi sincronizado, adicionar header
        if hasattr(request, "pwa_synced") and request.pwa_synced:
            response["X-Sync-Status"] = "synced"

        return response


class PWAVersionMiddleware(MiddlewareMixin):
    """
    Middleware para versionar PWA e invalidar cache quando necessário
    """

    def process_response(self, request, response):
        """Adicionar versão PWA aos headers"""

        pwa_version = getattr(settings, "PWA_VERSION", "1.0.0")
        response["X-PWA-Version"] = pwa_version

        # Adicionar cache-busting header
        if request.path.endswith(".js") or request.path.endswith(".css"):
            response["X-Cache-Buster"] = pwa_version

        return response
