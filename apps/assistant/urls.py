"""
URL configuration for Assistant app
"""

from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    # Chat UI endpoints
    path('', views.chat_interface, name='chat_interface'),
    
    # Chat API endpoints (HTMX)
    path('api/chat/message/', views.chat_message, name='chat_message'),
    path('api/chat/history/<int:conversation_id>/', views.chat_history, name='chat_history'),
    path('api/chat/new/', views.create_conversation, name='create_conversation'),
    
    # Document management
    path('api/documents/', views.list_documents, name='list_documents'),
    path('api/documents/ingest/', views.ingest_documents, name='ingest_documents'),
    
    # Health check
    path('api/health/', views.health_check, name='health_check'),
]
