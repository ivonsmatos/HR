"""
Django settings for SyncRH - DEVELOPMENT ENVIRONMENT

This settings file is for development only. Use environment variables for configuration.
Database: PostgreSQL (multi-tenant with schema isolation via django-tenants)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "ERRO CRÍTICO: SECRET_KEY não configurada em .env\n"
        "Configure: SECRET_KEY=seu-valor-aleatorio-seguro em .env"
    )

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False") == "True"
if DEBUG and not os.getenv("ALLOW_DEBUG_IN_PROD"):
    print("⚠️  WARNING: DEBUG=True em ambientes não-dev pode expor informações sensíveis")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
if not DEBUG and not os.getenv("ALLOWED_HOSTS"):
    raise ValueError(
        "ERRO CRÍTICO: ALLOWED_HOSTS não configurada em produção\n"
        "Configure: ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com em .env"
    )

# Application definition
DJANGO_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "celery",
]

LOCAL_APPS = [
    "apps.core",
    "apps.hrm",
    "apps.work",
    "apps.finance",
    "apps.crm",
    "apps.recruitment",
    "apps.security",
    "apps.security.zero_trust",  # Zero-Trust Security Architecture
    "apps.saas_admin",
    "apps.utilities",
    "apps.assistant",
    # HR Modules (Módulos de RH)
    "apps.departamento_pessoal",
    "apps.recrutamento_selecao",
    "apps.desenvolvimento_performance",
    "apps.engajamento_retencao",
    "apps.gestao_comportamental",
    # Compliance & Security Frameworks
    "apps.lgpd",  # Lei Geral de Proteção de Dados (13.709/2018)
    "apps.nist",  # NIST Cybersecurity Framework
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Configure TENANT_APPS for django-tenants (shared apps are not in TENANT_APPS)
TENANT_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Security Middlewares
    "apps.security.middleware.AuditoriaLoggingMiddleware",
    "apps.core.monitoring.PerformanceMiddleware",
    "apps.core.monitoring.PerformanceCheckMiddleware",
    # Zero-Trust Security Architecture (NIST SP 800-207)
    "apps.security.zero_trust.middleware.DeviceTrustMiddleware",
    "apps.security.zero_trust.middleware.RateLimitMiddleware",
    "apps.security.zero_trust.middleware.ZeroTrustMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.assistant.context_processors.helix_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "worksuite_db"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Custom user model (Usuário em apps/core/models.py)
AUTH_USER_MODEL = "core.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Whitenoise Configuration
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Django REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")

# Celery Configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Email Configuration
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

# Logging Configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}

# Sentry Configuration (Error Tracking)
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment=os.getenv("ENVIRONMENT", "development"),
    )

# Django Tenants Configuration
TENANT_MODEL = "core.Company"
TENANT_DOMAIN_MODEL = "core.CompanyDomain"

# ============================================================================
# ZERO-TRUST SECURITY CONFIGURATION (NIST SP 800-207)
# ============================================================================

ZERO_TRUST_CONFIG = {
    # Risk Score Thresholds
    "RISK_THRESHOLDS": {
        "ALLOW": 70,          # Score >= 70: Allow access
        "MONITOR": 50,        # Score 50-70: Allow with monitoring
        "CHALLENGE": 30,      # Score 30-50: Require MFA
        "DENY": 0,            # Score < 30: Deny access
    },
    
    # Continuous Authentication Settings
    "CONTINUOUS_AUTH": {
        "SESSION_TIMEOUT_MINUTES": 480,      # 8 hours
        "CONFIDENCE_DECAY_MINUTES": 15,      # Decay interval
        "CONFIDENCE_DECAY_POINTS": 5,        # Points per interval
        "MIN_CONFIDENCE_SCORE": 40,          # Below this requires re-auth
        "MAX_IDLE_MINUTES": 30,              # Idle timeout
    },
    
    # Device Trust Settings
    "DEVICE_TRUST": {
        "FINGERPRINT_COMPONENTS": [
            "user_agent",
            "accept_language",
            "accept_encoding",
            "timezone",
            "screen_resolution",
        ],
        "ELEVATION_REQUIREMENTS": {
            "basic_to_elevated": {
                "min_days_registered": 7,
                "min_successful_logins": 10,
                "mfa_required": True,
            },
            "elevated_to_corporate": {
                "min_days_registered": 30,
                "admin_approval_required": True,
                "compliance_training_completed": True,
            },
        },
    },
    
    # Rate Limiting
    "RATE_LIMITING": {
        "DEFAULT_RATE": "1000/hour",
        "LOGIN_RATE": "5/minute",
        "API_RATE": "100/minute",
        "SENSITIVE_RATE": "10/minute",
    },
    
    # Exempt Paths (no Zero-Trust validation)
    "EXEMPT_PATHS": [
        "/api/auth/login/",
        "/api/auth/register/",
        "/admin/login/",
        "/static/",
        "/media/",
        "/api/pwa/",
        "/health/",
        "/favicon.ico",
    ],
    
    # Sensitive Resources (require elevated trust)
    "SENSITIVE_RESOURCES": [
        "/api/lgpd/",
        "/api/nist/",
        "/api/security/",
        "/admin/",
        "/api/finance/",
        "/api/payroll/",
    ],
    
    # Geographic Restrictions
    "GEO_RESTRICTIONS": {
        "ALLOWED_COUNTRIES": ["BR", "US", "PT"],  # Empty = all allowed
        "BLOCKED_COUNTRIES": [],
        "HIGH_RISK_COUNTRIES": ["RU", "CN", "KP", "IR"],
    },
    
    # Behavioral Analysis
    "BEHAVIORAL_ANALYSIS": {
        "ENABLED": True,
        "ANOMALY_THRESHOLD": 2.0,  # Standard deviations
        "BASELINE_DAYS": 30,
        "FEATURES": [
            "login_time",
            "request_frequency",
            "resource_patterns",
            "device_usage",
            "location_patterns",
        ],
    },
}

# ============================================================================
# PWA CONFIGURATION
# ============================================================================

PWA_CONFIG = {
    "APP_NAME": "SyncRH",
    "APP_DESCRIPTION": "Sistema de Gestão de Recursos Humanos",
    "APP_THEME_COLOR": "#2563eb",
    "APP_BACKGROUND_COLOR": "#ffffff",
    "APP_DISPLAY": "standalone",
    "APP_SCOPE": "/",
    "APP_ORIENTATION": "portrait-primary",
    "APP_START_URL": "/",
    "APP_STATUS_BAR_COLOR": "default",
    "APP_ICONS": [
        {"src": "/static/images/icons/icon-72x72.png", "sizes": "72x72", "type": "image/png"},
        {"src": "/static/images/icons/icon-96x96.png", "sizes": "96x96", "type": "image/png"},
        {"src": "/static/images/icons/icon-128x128.png", "sizes": "128x128", "type": "image/png"},
        {"src": "/static/images/icons/icon-144x144.png", "sizes": "144x144", "type": "image/png"},
        {"src": "/static/images/icons/icon-152x152.png", "sizes": "152x152", "type": "image/png"},
        {"src": "/static/images/icons/icon-192x192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "/static/images/icons/icon-384x384.png", "sizes": "384x384", "type": "image/png"},
        {"src": "/static/images/icons/icon-512x512.png", "sizes": "512x512", "type": "image/png"},
    ],
    "APP_SPLASH_SCREEN": [],
    "APP_DIR": "ltr",
    "APP_LANG": "pt-BR",
}
