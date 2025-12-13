"""
SyncRH - Security Module
========================
Módulo de segurança com:
- Auditoria de logs
- Zero-Trust Architecture
"""

# Lazy imports para evitar importação circular
# Use: from apps.security.middleware import AuditoriaLoggingMiddleware

__all__ = ['AuditoriaLoggingMiddleware']

def __getattr__(name):
    if name == 'AuditoriaLoggingMiddleware':
        from .middleware import AuditoriaLoggingMiddleware
        return AuditoriaLoggingMiddleware
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
