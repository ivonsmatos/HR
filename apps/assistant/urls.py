"""
URL configuration for Assistant app
"""

from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    # Chat endpoints
    path('api/chat/message/', views.chat_message, name='chat_message'),
    path('api/chat/history/<int:conversation_id>/', views.get_conversation_history, name='conversation_history'),
    path('api/chat/new/', views.create_conversation, name='create_conversation'),
    
    # Document management
    path('api/documents/', views.list_documents, name='list_documents'),
    path('api/documents/ingest/', views.ingest_documents, name='ingest_documents'),
    
    # UI endpoints
    path('chat/', views.chat_interface, name='chat_interface'),
    path('chat/window/', views.chat_window, name='chat_window'),
]
