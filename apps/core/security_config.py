"""
SyncRH - Configurações de Segurança
===================================
Configurações centralizadas de segurança para produção
"""

# Middleware de segurança a adicionar em settings.py
SECURITY_MIDDLEWARE = [
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.RateLimitMiddleware',
    'apps.core.middleware.AuditLogMiddleware',
    'apps.core.middleware.RequestValidationMiddleware',
    'apps.core.middleware.SessionSecurityMiddleware',
]

# Configurações de Rate Limiting
RATE_LIMIT_CONFIG = {
    'RATE_LIMIT_REQUESTS': 100,  # requisições máximas
    'RATE_LIMIT_WINDOW': 60,     # por minuto
}

# Configurações de Sessão
SESSION_CONFIG = {
    'SESSION_INACTIVITY_TIMEOUT': 30 * 60,  # 30 minutos
    'SESSION_COOKIE_SECURE': True,          # Apenas HTTPS
    'SESSION_COOKIE_HTTPONLY': True,        # Não acessível via JS
    'SESSION_COOKIE_SAMESITE': 'Lax',       # Proteção CSRF
}

# Configurações CORS para produção
CORS_CONFIG = {
    'CORS_ALLOWED_ORIGINS': [
        # Adicionar domínios permitidos
    ],
    'CORS_ALLOW_CREDENTIALS': True,
    'CORS_ALLOW_METHODS': [
        'DELETE',
        'GET',
        'OPTIONS',
        'PATCH',
        'POST',
        'PUT',
    ],
    'CORS_ALLOW_HEADERS': [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ],
}

# Configurações de Senhas
PASSWORD_CONFIG = {
    'AUTH_PASSWORD_VALIDATORS': [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
            'OPTIONS': {
                'min_length': 10,
            }
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ],
}

# Headers de Segurança
SECURITY_HEADERS = {
    'SECURE_BROWSER_XSS_FILTER': True,
    'SECURE_CONTENT_TYPE_NOSNIFF': True,
    'X_FRAME_OPTIONS': 'DENY',
    'SECURE_HSTS_SECONDS': 31536000,
    'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
    'SECURE_HSTS_PRELOAD': True,
    'SECURE_SSL_REDIRECT': True,  # Apenas em produção
}

# Configurações de Logging para Auditoria
AUDIT_LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'audit': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'audit_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/audit.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'audit',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/security.log',
            'maxBytes': 10485760,
            'backupCount': 10,
            'formatter': 'audit',
        },
    },
    'loggers': {
        'audit': {
            'handlers': ['audit_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Configurações REST Framework para Segurança
REST_FRAMEWORK_SECURITY = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/minute',
        'user': '100/minute',
    },
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# Configurações JWT
JWT_CONFIG = {
    'ACCESS_TOKEN_LIFETIME': 15,      # minutos
    'REFRESH_TOKEN_LIFETIME': 1440,   # 24 horas
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': None,  # Usar SECRET_KEY do Django
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# IPs permitidos para admin (vazio = todos permitidos)
ADMIN_IP_WHITELIST = [
    # '127.0.0.1',
    # '10.0.0.0/8',
]

# Configurações de Upload
UPLOAD_CONFIG = {
    'MAX_UPLOAD_SIZE': 10 * 1024 * 1024,  # 10MB
    'ALLOWED_UPLOAD_EXTENSIONS': [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.jpg', '.jpeg', '.png', '.gif',
        '.txt', '.csv'
    ],
}


def apply_security_settings(settings_module):
    """
    Aplica configurações de segurança ao módulo settings.
    
    Uso em settings.py:
        from apps.core.security_config import apply_security_settings
        apply_security_settings(globals())
    """
    import os
    
    # Determina ambiente
    is_production = not settings_module.get('DEBUG', True)
    
    # Headers de segurança (apenas em produção)
    if is_production:
        settings_module.update(SECURITY_HEADERS)
    
    # Rate limiting
    settings_module.update(RATE_LIMIT_CONFIG)
    
    # Sessão
    if is_production:
        settings_module.update(SESSION_CONFIG)
    
    # Senha
    settings_module['AUTH_PASSWORD_VALIDATORS'] = PASSWORD_CONFIG['AUTH_PASSWORD_VALIDATORS']
    
    # Adiciona middleware de segurança
    middleware = settings_module.get('MIDDLEWARE', [])
    for mw in reversed(SECURITY_MIDDLEWARE):
        if mw not in middleware:
            # Adiciona após SecurityMiddleware do Django
            try:
                idx = middleware.index('django.middleware.security.SecurityMiddleware')
                middleware.insert(idx + 1, mw)
            except ValueError:
                middleware.insert(0, mw)
    settings_module['MIDDLEWARE'] = middleware
    
    # Cria diretório de logs se não existir
    logs_dir = os.path.join(settings_module.get('BASE_DIR', '.'), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
