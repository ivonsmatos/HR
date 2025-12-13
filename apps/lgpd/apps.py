"""
SyncRH - Configuração do App LGPD
"""

from django.apps import AppConfig


class LgpdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.lgpd'
    verbose_name = 'LGPD - Proteção de Dados'
    
    def ready(self):
        # Importa signals se necessário
        pass
