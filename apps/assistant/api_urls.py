"""
API URL Configuration for Helix

REST endpoints:
- /api/helix/documents/ - Document management
- /api/helix/conversations/ - Conversation management
- /api/helix/messages/ - Message management

GraphQL:
- /graphql/ - GraphQL endpoint
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    DocumentViewSet,
    DocumentChunkViewSet,
    ConversationViewSet,
    MessageViewSet,
)

# Create router for viewsets
router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'chunks', DocumentChunkViewSet, basename='chunk')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

app_name = 'api_helix'

urlpatterns = [
    path('', include(router.urls)),
]
