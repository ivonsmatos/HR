#!/usr/bin/env python
"""
PWA Settings Integration
Add this to config/settings.py after importing from config.pwa

This file shows how to integrate PWA with Django settings
"""

# Add to INSTALLED_APPS
PWA_INSTALLED_APPS = [
    # "pwa",  # Optional: django-pwa package
]

# Add to MIDDLEWARE (at the top for better performance)
PWA_MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Add before SecurityMiddleware
]

# PWA HTTP Headers
PWA_HTTP_HEADERS = {
    # Service Worker Cache-Control
    "Service-Worker-Allowed": "/",
    "Cache-Control": "public, max-age=3600",
}

# PWA Development Settings
PWA_DEV_SETTINGS = {
    "debug": False,  # Set to True in development
    "sw_prefix": "/static/js/",
    "service_worker_file": "service-worker.js",
    "pwa_js_file": "pwa.js",
}

# PWA Template Context Processor
def pwa_context_processor(request):
    """Add PWA context to all templates"""
    from config.pwa import (
        PWA_APP_NAME,
        PWA_APP_THEME_COLOR,
        PWA_APP_DISPLAY,
    )

    return {
        "pwa_app_name": PWA_APP_NAME,
        "pwa_theme_color": PWA_APP_THEME_COLOR,
        "pwa_display": PWA_APP_DISPLAY,
        "is_pwa": request.META.get("HTTP_X_PWA") == "true",
    }


# How to use in settings.py:

# 1. Add to INSTALLED_APPS:
# INSTALLED_APPS = [
#     ...
#     "whitenoise.apps.WhiteNoiseAppConfig",  # Enable before other apps
# ]

# 2. Add to MIDDLEWARE (at top):
# MIDDLEWARE = [
#     "whitenoise.middleware.WhiteNoiseMiddleware",
#     "django.middleware.security.SecurityMiddleware",
#     ...
# ]

# 3. Add static files configuration:
# STATIC_URL = "/static/"
# STATIC_ROOT = BASE_DIR / "staticfiles"
# STATICFILES_DIRS = [
#     BASE_DIR / "static",
# ]
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# 4. Add templates context processors:
# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 ...
#                 "config.pwa_settings.pwa_context_processor",
#             ],
#         },
#     },
# ]

# 5. Add PWA security headers:
# SECURE_SSL_REDIRECT = not DEBUG
# SESSION_COOKIE_SECURE = not DEBUG
# CSRF_COOKIE_SECURE = not DEBUG
# SECURE_BROWSER_XSS_FILTER = True
# SECURE_CONTENT_SECURITY_POLICY = {
#     "default-src": ("'self'",),
#     "script-src": ("'self'", "'unsafe-inline'"),
#     "img-src": ("'self'", "data:", "https:"),
#     "style-src": ("'self'", "'unsafe-inline'"),
#     "font-src": ("'self'", "data:", "https:"),
# }

# 6. Import PWA config at the end:
# from config.pwa import *
