"""
Context Processor for Helix Assistant

Provides global context variables to all templates:
- helix_status: System health check (Ollama running, models available, etc)
- has_conversations: Whether user has active conversations
- current_conversation: Current conversation (if any)
"""

import logging
from .services import get_helix_status, check_ollama_connection
from .models import Conversa

logger = logging.getLogger(__name__)


def helix_context(request):
    """
    Global context processor for Helix Assistant
    
    Available in all templates as:
    - {{ helix.status }} - System status dict
    - {{ helix.ollama_available }} - Boolean
    - {{ helix.models_available }} - List of model names
    - {{ helix.has_conversations }} - Boolean
    - {{ helix.current_conversation }} - Current conversation or None
    """
    context = {
        'helix': {
            'status': {},
            'ollama_available': False,
            'models_available': [],
            'has_conversations': False,
            'current_conversation': None,
            'user_authenticated': request.user.is_authenticated,
        }
    }
    
    # Only process if user is authenticated
    if not request.user.is_authenticated:
        return context
    
    try:
        # Get system status
        status = get_helix_status()
        context['helix']['status'] = status
        context['helix']['ollama_available'] = status.get('ollama_running', False)
        context['helix']['models_available'] = status.get('models_available', [])
        
        # Check for user's conversations
        # Get company from user if available (multi-tenant)
        filter_kwargs = {
            'user': request.user,
            'is_active': True
        }
        
        # Add company filter if user has tenant attribute
        if hasattr(request.user, 'tenant') and request.user.tenant:
            filter_kwargs['company'] = request.user.tenant
        elif hasattr(request.user, 'company') and request.user.company:
            filter_kwargs['company'] = request.user.company
        
        conversations = Conversa.objects.filter(**filter_kwargs).first()
        
        if conversations:
            context['helix']['has_conversations'] = True
            context['helix']['current_conversation'] = conversations
        
        logger.debug(f"Helix context loaded for {request.user}: {context['helix']['ollama_available']}")
        
    except Exception as e:
        logger.warning(f"Erro loading Helix context: {e}")
        # Continuar gracefully if there's an error
        context['helix']['status'] = {'error': str(e)}
    
    return context
