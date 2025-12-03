"""
Security middleware para Worksuite PWA

Implementa:
- Rate limiting
- Security headers
- CORS validation
- IP blocking
- Request logging
"""

import logging
from django.conf import settings
from django.http import JsonResponse
from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.middleware.security import SecurityMiddleware
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting por IP
    
    Configuração em .env:
    RATELIMIT_ENABLE=True
    RATELIMIT_REQUESTS_PER_HOUR=1000
    """
    
    def process_request(self, request):
        if not settings.DEBUG and getattr(settings, 'RATELIMIT_ENABLE', True):
            client_ip = self.get_client_ip(request)
            key = f"ratelimit:{client_ip}"
            
            limit = getattr(settings, 'RATELIMIT_REQUESTS_PER_HOUR', 1000)
            current = cache.get(key, 0)
            
            if current >= limit:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JsonResponse(
                    {"error": "Too many requests. Try again later."},
                    status=429
                )
            
            cache.set(key, current + 1, 3600)  # 1 hora
    
    @staticmethod
    def get_client_ip(request):
        """Obter IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Adiciona headers de segurança"""
    
    def process_response(self, request, response):
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Conteúdo-Type-Options'] = 'nosniff'
        
        # Enable XSS filter
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Feature policy
        response['Permissions-Policy'] = (
            'geolocation=(), '
            'microphone=(), '
            'camera=(), '
            'payment=()'
        )
        
        # Conteúdo Security Policy
        if not settings.DEBUG:
            response['Conteúdo-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        
        return response


class SecurityAuditoriaLoggingMiddleware(MiddlewareMixin):
    """Log de eventos de segurança"""
    
    SECURITY_EVENTS = {
        'failed_login': 401,
        'permission_denied': 403,
        'rate_limited': 429,
    }
    
    def process_response(self, request, response):
        client_ip = RateLimitMiddleware.get_client_ip(request)
        
        # Log failed logins
        if response.status_code == 401 and request.path.endswith('/login/'):
            logger.warning(
                f"Failed login attempt | IP: {client_ip} | Usuário: {request.POST.get('username', 'unknown')}"
            )
        
        # Log permission denied
        elif response.status_code == 403:
            logger.warning(
                f"Permission denied | IP: {client_ip} | Path: {request.path} | Usuário: {request.user}"
            )
        
        # Log rate limited
        elif response.status_code == 429:
            logger.error(
                f"Rate limit exceeded | IP: {client_ip} | Path: {request.path}"
            )
        
        # Log suspicious patterns
        if request.path.startswith('/admin/') and response.status_code in [401, 403]:
            logger.warning(
                f"Admin access attempt | IP: {client_ip} | Status: {response.status_code}"
            )
        
        return response


class IPBlockingMiddleware(MiddlewareMixin):
    """Bloqueia IPs conhecidos como maliciosos"""
    
    def process_request(self, request):
        client_ip = RateLimitMiddleware.get_client_ip(request)
        
        # Verificar se IP está bloqueado
        blocked_ips = cache.get('blocked_ips', set())
        if client_ip in blocked_ips:
            logger.error(f"Blocked IP access attempt: {client_ip}")
            return JsonResponse(
                {"error": "Access denied"},
                status=403
            )
        
        return Nãone


class RequestIDMiddleware(MiddlewareMixin):
    """Adiciona request ID para rastreamento"""
    
    def process_request(self, request):
        import uuid
        request.id = str(uuid.uuid4())
    
    def process_response(self, request, response):
        response['X-Request-ID'] = getattr(request, 'id', 'unknown')
        return response


class SecurityValidationMiddleware(MiddlewareMixin):
    """Valida segurança de requests"""
    
    def process_request(self, request):
        # Validar Usuário-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        if not user_agent:
            logger.warning(f"Request without Usuário-Agent from {RateLimitMiddleware.get_client_ip(request)}")
        
        # Validar Conteúdo-Type para POST
        if request.method == 'POST':
            content_type = request.META.get('CONTENT_TYPE', '')
            if not content_type:
                logger.warning(f"POST without Conteúdo-Type from {RateLimitMiddleware.get_client_ip(request)}")
        
        return Nãone


# Utility functions para admin

def block_ip(ip_address, hours=24):
    """Bloquear um IP por N horas"""
    blocked_ips = cache.get('blocked_ips', set())
    blocked_ips.add(ip_address)
    cache.set('blocked_ips', blocked_ips, hours * 3600)
    logger.info(f"IP blocked: {ip_address} for {hours} hours")


def unblock_ip(ip_address):
    """Desbloquear um IP"""
    blocked_ips = cache.get('blocked_ips', set())
    blocked_ips.discard(ip_address)
    cache.set('blocked_ips', blocked_ips, 24 * 3600)
    logger.info(f"IP unblocked: {ip_address}")


def get_blocked_ips():
    """Retornar lista de IPs bloqueados"""
    return cache.get('blocked_ips', set())
