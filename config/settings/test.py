"""
Django settings for testing with SQLite (no PostgreSQL required)
"""
from . import *  # noqa

# Force SQLite for testing (no PostgreSQL needed)
import tempfile
import os
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(tempfile.gettempdir(), 'syncrh_dev.sqlite3'),
    }
}

# Remove django-tenants from INSTALLED_APPS (it requires PostgreSQL)
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'django_tenants' not in app]

# Simplified apps for development - skip problematic apps
PROBLEMATIC_APPS = [
    'apps.finance',
    'apps.recruitment', 
    'apps.utilities',
    'apps.departamento_pessoal',
    'apps.desenvolvimento_performance',
    'apps.engajamento_retencao',
    'apps.gestao_comportamental',
    'apps.recrutamento_selecao',
    'apps.lgpd',
    'apps.nist',
    'apps.crm',
    'apps.hrm',
    'apps.work',
    'apps.security.zero_trust',
]

INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in PROBLEMATIC_APPS]

# Use custom user model
AUTH_USER_MODEL = 'core.User'

# Remove all tenant-related middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'Tenant' not in m and 'Audit' not in m and 'Performance' not in m]

# Ensure SessionMiddleware and AuthenticationMiddleware are in MIDDLEWARE for admin
if 'django.contrib.sessions.middleware.SessionMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(0, 'django.contrib.sessions.middleware.SessionMiddleware')
if 'django.contrib.auth.middleware.AuthenticationMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'django.contrib.auth.middleware.AuthenticationMiddleware')

# Remove DATABASE_ROUTERS for tests
DATABASE_ROUTERS = []

# Configure tenant apps for django-tenants (not used in tests)
TENANT_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'rest_framework',
    'apps.core',
    'apps.security',
    'apps.hrm',
    'apps.work',
    'apps.assistant',
]

# Disable email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable celery for tests
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Set SECRET_KEY if not defined
SECRET_KEY = 'test-secret-key-do-not-use-in-production'

# Login settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'





