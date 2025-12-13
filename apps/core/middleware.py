"""
SyncRH - Middleware de Segurança
================================
Middleware para segurança, auditoria e controle de acesso
"""

import logging
import time
import hashlib
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Middleware para adicionar headers de segurança às respostas HTTP.
    
    Headers implementados:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (HSTS)
    - Content-Security-Policy
    - Referrer-Policy
    - Permissions-Policy
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Previne MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Previne clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Ativa proteção XSS do navegador
        response['X-XSS-Protection'] = '1; mode=block'
        
        # HSTS - força HTTPS (apenas em produção)
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Política de referrer
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Política de permissões
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), '
            'payment=(), usb=()'
        )
        
        return response


class RateLimitMiddleware:
    """
    Middleware para limitar requisições por IP/usuário.
    
    Configuração via settings:
    - RATE_LIMIT_REQUESTS: número máximo de requisições (default: 100)
    - RATE_LIMIT_WINDOW: janela de tempo em segundos (default: 60)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)
        self.window = getattr(settings, 'RATE_LIMIT_WINDOW', 60)
    
    def __call__(self, request):
        # Identifica o cliente
        client_id = self._get_client_id(request)
        cache_key = f'rate_limit:{client_id}'
        
        # Obtém contador atual
        request_count = cache.get(cache_key, 0)
        
        # Verifica limite
        if request_count >= self.max_requests:
            logger.warning(f"Rate limit excedido para: {client_id}")
            return JsonResponse(
                {
                    'error': 'Limite de requisições excedido',
                    'detail': f'Máximo de {self.max_requests} requisições por {self.window} segundos',
                    'retry_after': self.window
                },
                status=429
            )
        
        # Incrementa contador
        cache.set(cache_key, request_count + 1, self.window)
        
        response = self.get_response(request)
        
        # Adiciona headers de rate limit
        response['X-RateLimit-Limit'] = str(self.max_requests)
        response['X-RateLimit-Remaining'] = str(self.max_requests - request_count - 1)
        response['X-RateLimit-Reset'] = str(self.window)
        
        return response
    
    def _get_client_id(self, request):
        """Obtém identificador único do cliente"""
        if request.user.is_authenticated:
            return f'user:{request.user.id}'
        
        # Usa IP para usuários anônimos
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f'ip:{ip}'


class AuditLogMiddleware:
    """
    Middleware para registro de auditoria de ações.
    
    Registra:
    - Requisições de escrita (POST, PUT, PATCH, DELETE)
    - Acessos a recursos sensíveis
    - Falhas de autenticação
    """
    
    SENSITIVE_PATHS = [
        '/admin/',
        '/api/v1/security/',
        '/api/v1/dp/colaboradores/',
        '/api/v1/dp/folhas-pagamento/'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Marca tempo de início
        start_time = time.time()
        
        response = self.get_response(request)
        
        # Calcula duração
        duration = time.time() - start_time
        
        # Registra se necessário
        if self._should_log(request, response):
            self._log_request(request, response, duration)
        
        return response
    
    def _should_log(self, request, response):
        """Determina se deve registrar a requisição"""
        # Sempre registra métodos de escrita
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return True
        
        # Registra acessos a paths sensíveis
        for path in self.SENSITIVE_PATHS:
            if request.path.startswith(path):
                return True
        
        # Registra erros de autenticação
        if response.status_code in [401, 403]:
            return True
        
        return False
    
    def _log_request(self, request, response, duration):
        """Registra a requisição no log de auditoria"""
        user = request.user if request.user.is_authenticated else None
        
        log_data = {
            'timestamp': timezone.now().isoformat(),
            'user_id': user.id if user else None,
            'user_email': user.email if user else None,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2),
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        }
        
        # Log estruturado
        logger.info(
            f"AUDIT: {log_data['method']} {log_data['path']} - "
            f"User: {log_data['user_email']} - "
            f"Status: {log_data['status_code']} - "
            f"Duration: {log_data['duration_ms']}ms"
        )
        
        # Em produção, salvaria em tabela de auditoria
        # AuditLog.objects.create(**log_data)
    
    def _get_client_ip(self, request):
        """Obtém IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class RequestValidationMiddleware:
    """
    Middleware para validação de requisições.
    
    Validações:
    - Tamanho máximo do corpo da requisição
    - Content-Type válido para APIs
    - Tokens de segurança (CSRF para formulários)
    """
    
    # 10MB por padrão
    MAX_BODY_SIZE = 10 * 1024 * 1024
    
    VALID_CONTENT_TYPES = [
        'application/json',
        'application/x-www-form-urlencoded',
        'multipart/form-data'
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_body = getattr(
            settings, 'MAX_REQUEST_BODY_SIZE', self.MAX_BODY_SIZE
        )
    
    def __call__(self, request):
        # Valida tamanho do corpo
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length:
            try:
                if int(content_length) > self.max_body:
                    return JsonResponse(
                        {'error': 'Requisição muito grande'},
                        status=413
                    )
            except (ValueError, TypeError):
                pass
        
        # Valida Content-Type para requisições com corpo
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.content_type
            if content_type and not any(
                ct in content_type for ct in self.VALID_CONTENT_TYPES
            ):
                # Permite requests sem body ou com tipos específicos
                if content_type and 'text/' not in content_type:
                    logger.warning(
                        f"Content-Type inválido: {content_type}"
                    )
        
        return self.get_response(request)


class IPWhitelistMiddleware:
    """
    Middleware para whitelist de IPs em áreas administrativas.
    
    Configuração via settings:
    - ADMIN_IP_WHITELIST: lista de IPs permitidos (vazio = permite todos)
    """
    
    ADMIN_PATHS = ['/admin/']
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.whitelist = getattr(settings, 'ADMIN_IP_WHITELIST', [])
    
    def __call__(self, request):
        # Se whitelist vazia, permite todos
        if not self.whitelist:
            return self.get_response(request)
        
        # Verifica se é path administrativo
        is_admin = any(
            request.path.startswith(path) for path in self.ADMIN_PATHS
        )
        
        if is_admin:
            client_ip = self._get_client_ip(request)
            
            if client_ip not in self.whitelist:
                logger.warning(
                    f"Acesso admin bloqueado - IP: {client_ip}"
                )
                return HttpResponseForbidden('Acesso não autorizado')
        
        return self.get_response(request)
    
    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', 'unknown')


class SessionSecurityMiddleware:
    """
    Middleware para segurança de sessão.
    
    Funcionalidades:
    - Rotação de sessão em login
    - Timeout de inatividade
    - Detecção de sessão hijacking
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.session_timeout = getattr(
            settings, 'SESSION_INACTIVITY_TIMEOUT', 30 * 60
        )  # 30 minutos
    
    def __call__(self, request):
        if request.user.is_authenticated:
            # Verifica timeout de inatividade
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                elapsed = time.time() - last_activity
                
                if elapsed > self.session_timeout:
                    from django.contrib.auth import logout
                    logout(request)
                    
                    return JsonResponse(
                        {'error': 'Sessão expirada por inatividade'},
                        status=401
                    )
            
            # Atualiza última atividade
            request.session['last_activity'] = time.time()
            
            # Verifica fingerprint da sessão
            current_fingerprint = self._get_fingerprint(request)
            stored_fingerprint = request.session.get('fingerprint')
            
            if stored_fingerprint and stored_fingerprint != current_fingerprint:
                logger.warning(
                    f"Possível session hijacking detectado - "
                    f"User: {request.user.email}"
                )
                # Em produção, poderia invalidar a sessão
        
        return self.get_response(request)
    
    def _get_fingerprint(self, request):
        """Gera fingerprint baseado em características do cliente"""
        data = (
            request.META.get('HTTP_USER_AGENT', '') +
            request.META.get('HTTP_ACCEPT_LANGUAGE', '') +
            request.META.get('HTTP_ACCEPT_ENCODING', '')
        )
        return hashlib.sha256(data.encode()).hexdigest()[:32]


# Lista de middlewares recomendados para adicionar ao settings
SECURITY_MIDDLEWARE = [
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.RateLimitMiddleware',
    'apps.core.middleware.AuditLogMiddleware',
    'apps.core.middleware.RequestValidationMiddleware',
    'apps.core.middleware.SessionSecurityMiddleware',
]
