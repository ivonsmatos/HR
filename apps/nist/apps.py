"""
SyncRH - Configuração do App NIST
"""

from django.apps import AppConfig


class NistConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.nist'
    verbose_name = 'NIST - Cybersecurity Framework'
    
    def ready(self):
        # Importa signals se necessário
        pass
