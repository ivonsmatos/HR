"""
SyncRH - Zero-Trust Security Middleware
========================================
Middleware que implementa verificação Zero-Trust em cada requisição.

Fluxo:
1. Identificar dispositivo
2. Verificar contexto de acesso
3. Avaliar risco
4. Aplicar políticas
5. Decidir acesso
"""

import uuid
import hashlib
import logging
from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

logger = logging.getLogger('security.zero_trust')
User = get_user_model()


class ZeroTrustMiddleware:
    """
    Middleware Zero-Trust - "Never Trust, Always Verify"
    
    Avalia cada requisição baseado em:
    - Identidade do usuário
    - Dispositivo
    - Localização/IP
    - Horário
    - Comportamento
    - Recurso solicitado
    """
    
    # Paths que ignoram verificação (login, assets, etc)
    EXEMPT_PATHS = [
        '/api/auth/login/',
        '/api/auth/token/',
        '/api/auth/refresh/',
        '/admin/login/',
        '/static/',
        '/media/',
        '/api/pwa/',
        '/health/',
        '/__debug__/',
    ]
    
    # Recursos sensíveis que requerem verificação extra
    SENSITIVE_RESOURCES = {
        '/api/lgpd/': 'high',
        '/api/nist/': 'high',
        '/api/security/': 'high',
        '/admin/': 'elevated',
        '/api/finance/': 'elevated',
        '/api/hrm/employees/': 'elevated',
        '/api/users/': 'elevated',
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Gerar request ID único
        request.zero_trust_id = str(uuid.uuid4())
        
        # Verificar se path está isento
        if self._is_exempt(request.path):
            return self.get_response(request)
        
        # Coletar contexto
        context = self._collect_context(request)
        
        # Avaliar risco
        risk_score, risk_factors = self._evaluate_risk(request, context)
        context['risk_score'] = risk_score
        context['risk_factors'] = risk_factors
        
        # Aplicar políticas
        decision, reason = self._apply_policies(request, context)
        
        # Registrar contexto de acesso
        self._log_access_context(request, context, decision, reason)
        
        # Executar decisão
        if decision == 'deny':
            return self._deny_access(request, reason)
        elif decision == 'challenge':
            return self._challenge_mfa(request, reason)
        elif decision == 'step_up':
            return self._require_step_up(request, reason)
        
        # Permitir acesso
        response = self.get_response(request)
        
        # Adicionar headers de segurança
        response = self._add_security_headers(response, context)
        
        return response
    
    def _is_exempt(self, path):
        """Verifica se path está isento de verificação."""
        for exempt in self.EXEMPT_PATHS:
            if path.startswith(exempt):
                return True
        return False
    
    def _collect_context(self, request):
        """Coleta contexto completo da requisição."""
        context = {
            'request_id': request.zero_trust_id,
            'timestamp': timezone.now(),
            'ip_address': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'method': request.method,
            'path': request.path,
            'is_authenticated': request.user.is_authenticated,
            'user_id': request.user.id if request.user.is_authenticated else None,
        }
        
        # Identificar dispositivo
        context['device_fingerprint'] = self._generate_fingerprint(request)
        
        # Identificar tipo de IP
        context['ip_type'] = self._classify_ip(context['ip_address'])
        
        # Verificar horário
        context['is_business_hours'] = self._is_business_hours()
        
        # Identificar sensibilidade do recurso
        context['resource_sensitivity'] = self._get_resource_sensitivity(request.path)
        
        # PWA context
        context['is_pwa'] = request.META.get('HTTP_X_PWA', 'false') == 'true'
        
        return context
    
    def _get_client_ip(self, request):
        """Extrai IP real do cliente."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')
    
    def _generate_fingerprint(self, request):
        """Gera fingerprint do dispositivo."""
        components = [
            request.META.get('HTTP_USER_AGENT', ''),
            request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
            request.META.get('HTTP_ACCEPT_ENCODING', ''),
            request.META.get('HTTP_SEC_CH_UA', ''),
            request.META.get('HTTP_SEC_CH_UA_PLATFORM', ''),
        ]
        raw = '|'.join(components)
        return hashlib.sha256(raw.encode()).hexdigest()[:32]
    
    def _classify_ip(self, ip):
        """Classifica tipo de IP."""
        # Simplificado - em produção usar GeoIP
        if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'):
            return 'private'
        if ip.startswith('127.'):
            return 'localhost'
        return 'public'
    
    def _is_business_hours(self):
        """Verifica se está em horário comercial."""
        now = timezone.localtime()
        # Segunda a Sexta, 7h às 20h
        if now.weekday() < 5 and 7 <= now.hour <= 20:
            return True
        return False
    
    def _get_resource_sensitivity(self, path):
        """Determina sensibilidade do recurso."""
        for pattern, level in self.SENSITIVE_RESOURCES.items():
            if path.startswith(pattern):
                return level
        return 'normal'
    
    def _evaluate_risk(self, request, context):
        """
        Avalia risco da requisição (0-100).
        Quanto maior, mais arriscado.
        """
        score = 0
        factors = []
        
        # 1. Usuário não autenticado acessando recurso protegido
        if not context['is_authenticated'] and context['resource_sensitivity'] != 'normal':
            score += 50
            factors.append('unauthenticated_sensitive_access')
        
        # 2. Acesso fora do horário comercial
        if not context['is_business_hours'] and context['is_authenticated']:
            score += 15
            factors.append('outside_business_hours')
        
        # 3. Recurso muito sensível
        if context['resource_sensitivity'] == 'high':
            score += 20
            factors.append('high_sensitivity_resource')
        elif context['resource_sensitivity'] == 'elevated':
            score += 10
            factors.append('elevated_sensitivity_resource')
        
        # 4. IP público (não corporativo)
        if context['ip_type'] == 'public':
            score += 10
            factors.append('public_ip')
        
        # 5. Verificar rate limiting
        if self._is_rate_limited(context):
            score += 30
            factors.append('rate_limit_approaching')
        
        # 6. Verificar dispositivo conhecido
        if context['is_authenticated']:
            if not self._is_known_device(request.user.id, context['device_fingerprint']):
                score += 20
                factors.append('unknown_device')
        
        # 7. Verificar IP na lista negra
        if self._is_ip_blocked(context['ip_address']):
            score += 100
            factors.append('blocked_ip')
        
        # Normalizar score (0-100)
        score = min(100, score)
        
        return score, factors
    
    def _is_rate_limited(self, context):
        """Verifica se está chegando perto do rate limit."""
        if not context['is_authenticated']:
            key = f"rl:ip:{context['ip_address']}"
        else:
            key = f"rl:user:{context['user_id']}"
        
        count = cache.get(key, 0)
        return count > 50  # Threshold de alerta
    
    def _is_known_device(self, user_id, fingerprint):
        """Verifica se dispositivo é conhecido."""
        cache_key = f"known_device:{user_id}:{fingerprint}"
        return cache.get(cache_key, False)
    
    def _is_ip_blocked(self, ip):
        """Verifica se IP está bloqueado."""
        cache_key = f"blocked_ip:{ip}"
        if cache.get(cache_key):
            return True
        
        # Verificar no banco (com cache)
        try:
            from apps.security.models import IpBlocklist
            is_blocked = IpBlocklist.objects.filter(
                ip_address=ip,
                is_active=True
            ).exists()
            if is_blocked:
                cache.set(cache_key, True, 300)  # Cache por 5 min
            return is_blocked
        except Exception:
            return False
    
    def _apply_policies(self, request, context):
        """
        Aplica políticas de segurança e retorna decisão.
        """
        risk_score = context['risk_score']
        
        # Bloquear se IP na lista negra
        if 'blocked_ip' in context.get('risk_factors', []):
            return 'deny', 'IP address is blocked'
        
        # Score crítico = negar
        if risk_score >= 80:
            return 'deny', f'Risk score too high: {risk_score}'
        
        # Score alto = solicitar MFA
        if risk_score >= 60:
            if context['is_authenticated'] and self._has_active_mfa(request.user):
                return 'allow', 'MFA already verified'
            return 'challenge', f'High risk score: {risk_score}'
        
        # Recurso sensível + risco médio = step-up auth
        if context['resource_sensitivity'] in ['high', 'elevated'] and risk_score >= 40:
            return 'step_up', 'Sensitive resource requires additional verification'
        
        # Default: permitir
        return 'allow', 'Within acceptable risk threshold'
    
    def _has_active_mfa(self, user):
        """Verifica se usuário tem MFA ativo e verificado na sessão."""
        # Implementação simplificada
        return False
    
    def _log_access_context(self, request, context, decision, reason):
        """Registra contexto de acesso para auditoria."""
        logger.info(
            f"ZeroTrust Access | "
            f"RequestID: {context['request_id']} | "
            f"User: {context.get('user_id', 'anon')} | "
            f"IP: {context['ip_address']} | "
            f"Path: {context['path']} | "
            f"Risk: {context['risk_score']} | "
            f"Decision: {decision} | "
            f"Reason: {reason}"
        )
        
        # Em produção, salvar no banco assincronamente
        # AccessContext.objects.create(...)
    
    def _deny_access(self, request, reason):
        """Retorna resposta de acesso negado."""
        logger.warning(f"Access DENIED: {request.zero_trust_id} - {reason}")
        return JsonResponse({
            'error': 'access_denied',
            'message': 'Access denied by security policy',
            'request_id': request.zero_trust_id,
        }, status=403)
    
    def _challenge_mfa(self, request, reason):
        """Solicita verificação MFA."""
        return JsonResponse({
            'error': 'mfa_required',
            'message': 'Multi-factor authentication required',
            'request_id': request.zero_trust_id,
            'redirect': '/auth/mfa/verify/',
        }, status=401)
    
    def _require_step_up(self, request, reason):
        """Solicita autenticação adicional."""
        return JsonResponse({
            'error': 'step_up_required',
            'message': 'Additional authentication required for this resource',
            'request_id': request.zero_trust_id,
            'redirect': '/auth/step-up/',
        }, status=401)
    
    def _add_security_headers(self, response, context):
        """Adiciona headers de segurança à resposta."""
        response['X-Request-ID'] = context['request_id']
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP para PWA
        if context.get('is_pwa'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "
                "manifest-src 'self';"
            )
        
        return response


class DeviceTrustMiddleware:
    """
    Middleware para gerenciar confiança de dispositivos.
    Deve vir DEPOIS do ZeroTrustMiddleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated:
            self._track_device(request)
        
        return self.get_response(request)
    
    def _track_device(self, request):
        """Registra/atualiza dispositivo do usuário."""
        fingerprint = getattr(request, 'device_fingerprint', None)
        if not fingerprint:
            return
        
        # Atualizar cache de dispositivo conhecido
        cache_key = f"known_device:{request.user.id}:{fingerprint}"
        cache.set(cache_key, True, 86400)  # 24 horas


class RateLimitMiddleware:
    """
    Rate limiting por usuário/IP.
    Zero-Trust: limitar mesmo usuários autenticados.
    """
    
    LIMITS = {
        'anonymous': {
            'per_minute': 30,
            'per_hour': 300,
        },
        'authenticated': {
            'per_minute': 100,
            'per_hour': 2000,
        },
        'api': {
            'per_minute': 60,
            'per_hour': 1000,
        }
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Determinar tipo de cliente
        if request.path.startswith('/api/'):
            client_type = 'api'
        elif request.user.is_authenticated:
            client_type = 'authenticated'
        else:
            client_type = 'anonymous'
        
        # Verificar limite
        is_limited, retry_after = self._check_rate_limit(request, client_type)
        
        if is_limited:
            response = JsonResponse({
                'error': 'rate_limit_exceeded',
                'message': 'Too many requests',
                'retry_after': retry_after,
            }, status=429)
            response['Retry-After'] = str(retry_after)
            return response
        
        return self.get_response(request)
    
    def _check_rate_limit(self, request, client_type):
        """Verifica e incrementa contadores de rate limit."""
        limits = self.LIMITS[client_type]
        
        # Identificador do cliente
        if request.user.is_authenticated:
            client_id = f"user:{request.user.id}"
        else:
            ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            ip = ip or request.META.get('REMOTE_ADDR', 'unknown')
            client_id = f"ip:{ip}"
        
        # Verificar limite por minuto
        minute_key = f"rl:{client_id}:minute"
        minute_count = cache.get(minute_key, 0)
        
        if minute_count >= limits['per_minute']:
            return True, 60
        
        # Verificar limite por hora
        hour_key = f"rl:{client_id}:hour"
        hour_count = cache.get(hour_key, 0)
        
        if hour_count >= limits['per_hour']:
            return True, 3600
        
        # Incrementar contadores
        cache.set(minute_key, minute_count + 1, 60)
        cache.set(hour_key, hour_count + 1, 3600)
        
        return False, 0
