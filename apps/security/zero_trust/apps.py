"""
============================================================================
Zero-Trust Security - Django App Configuration
============================================================================

Configuração do app Django para o módulo Zero-Trust Security.

@version 1.0.0
"""

from django.apps import AppConfig


class ZeroTrustConfig(AppConfig):
    """
    Configuração do app Zero-Trust Security.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.security.zero_trust'
    label = 'zero_trust'
    verbose_name = 'Zero-Trust Security'
    
    def ready(self):
        """
        Hook executado quando o app está pronto.
        Registra signals e inicializa componentes.
        """
        # Import signals
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass
