"""
API URL Configuração for Helix

REST endpoints:
- /api/helix/documents/ - Documento management
- /api/helix/conversations/ - Conversa management
- /api/helix/messages/ - Mensagem management

GraphQL:
- /graphql/ - GraphQL endpoint
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    DocumentoViewSet,
    DocumentoChunkViewSet,
    ConversaViewSet,
    MensagemViewSet,
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'documents', DocumentoViewSet, basename='document')
router.register(r'chunks', DocumentoChunkViewSet, basename='chunk')
router.register(r'conversations', ConversaViewSet, basename='conversation')
router.register(r'messages', MensagemViewSet, basename='message')

app_name = 'api_helix'

urlpatterns = [
    path('', include(router.urls)),
]
