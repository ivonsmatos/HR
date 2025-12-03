"""
Django App Configuração for Assistant (SyncRH)
RAG-based conversational agent for internal support
"""

from django.apps import AppConfig


class AssistantConfig(AppConfig):
    """Configuração for the Assistant application"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.assistant'
    verbose_name = 'Assistente SyncRH (RAG Assistant)'
    
    def ready(self):
        """Initialize app signals and setup"""
        # Importar signals when app is ready
        try:
            from . import signals  # noqa
        except ImportarErro:
            pass
