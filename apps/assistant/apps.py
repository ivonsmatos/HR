"""
Django App Configuration for Assistant (Helix Secretary)
RAG-based conversational agent for internal support
"""

from django.apps import AppConfig


class AssistantConfig(AppConfig):
    """Configuration for the Assistant application"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.assistant'
    verbose_name = 'Helix Secretary (RAG Assistant)'
    
    def ready(self):
        """Initialize app signals and setup"""
        # Import signals when app is ready
        try:
            from . import signals  # noqa
        except ImportError:
            pass
