"""
Django settings for testing with SQLite (no PostgreSQL required)
"""
from . import *  # noqa

# Force SQLite for testing (no PostgreSQL needed)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Remove django-tenants from INSTALLED_APPS (it requires PostgreSQL)
INSTALLED_APPS = [app for app in INSTALLED_APPS if 'django_tenants' not in app]

# Remove all tenant-related middleware
MIDDLEWARE = [m for m in MIDDLEWARE if 'Tenant' not in m and 'Audit' not in m and 'Performance' not in m]

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

# Disable migrations for faster testing
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Disable email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable celery for tests
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True

# Set SECRET_KEY if not defined
SECRET_KEY = 'test-secret-key-do-not-use-in-production'





