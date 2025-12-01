"""
Views for Assistant (Helix Secretary) - FASE C (UI/HTMX)

This module will contain:
- Chat endpoints for message handling
- Document management endpoints
- UI rendering with HTMX
- RAG query processing

NOTE: Implementation in Fase C - currently stubs
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message, Document


# ===== Chat Endpoints (HTMX) =====

@login_required
@require_http_methods(["GET"])
def chat_interface(request):
    """
    Main chat interface page
    Displays conversation list and chat window
    
    Fase C: Implement HTMX integration
    """
    conversations = Conversation.objects.filter(
        user=request.user,
        company=request.user.tenant
    ).order_by('-created_at')
    
    context = {
        'conversations': conversations,
    }
    return render(request, 'assistant/chat_interface.html', context)


@login_required
@require_http_methods(["GET"])
def chat_window(request):
    """
    Chat window component for HTMX requests
    Returns HTML fragment for chat widget
    
    Fase C: Implement HTMX hx-request handling
    """
    conversation_id = request.GET.get('conversation_id')
    
    if conversation_id:
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )
        messages = conversation.messages.all().order_by('created_at')
    else:
        messages = []
    
    context = {
        'conversation': conversation if conversation_id else None,
        'messages': messages,
    }
    return render(request, 'assistant/chat_window.html', context)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_message(request):
    """
    Handle chat messages from HTMX
    
    POST /api/chat/message/
    {
        "conversation_id": 123,
        "message": "What is the company policy on..."
    }
    
    Fase B: Implement RAG pipeline
    Fase C: Return HTMX fragment
    """
    # TODO: Fase B - Implement RAG query processing
    # TODO: Fase C - Return HTMX-compatible response
    
    return JsonResponse({
        'status': 'stub',
        'message': 'Chat endpoint - implement in Fase B/C'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_history(request, conversation_id):
    """
    Retrieve conversation history
    
    GET /api/chat/history/123/
    
    Fase C: Return HTMX fragment or JSON
    """
    conversation = get_object_or_404(
        Conversation,
        id=conversation_id,
        user=request.user
    )
    
    messages = list(
        conversation.messages.values(
            'id', 'role', 'content', 'created_at'
        ).order_by('created_at')
    )
    
    return JsonResponse({
        'conversation_id': conversation_id,
        'messages': messages,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_conversation(request):
    """
    Create a new conversation
    
    POST /api/chat/new/
    {
        "title": "Setup Questions"  # optional
    }
    
    Fase C: Implement conversation creation
    """
    title = request.data.get('title', 'New Conversation')
    
    conversation = Conversation.objects.create(
        user=request.user,
        company=request.user.tenant,
        title=title,
    )
    
    return JsonResponse({
        'conversation_id': conversation.id,
        'title': conversation.title,
    })


# ===== Document Management Endpoints =====

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_documents(request):
    """
    List all documents available for RAG
    
    GET /api/documents/
    
    Fase B: Filter by company and active status
    """
    documents = Document.objects.filter(
        company=request.user.tenant,
        is_active=True
    ).values('id', 'title', 'source_path', 'content_type')
    
    return JsonResponse({
        'documents': list(documents)
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ingest_documents(request):
    """
    Ingest documents from docs/ folder
    
    POST /api/documents/ingest/
    
    Fase B: Implement document chunking and embedding
    """
    # TODO: Fase B - Implement:
    # 1. Read docs/ folder
    # 2. Parse markdown/text/html
    # 3. Chunk text with overlap
    # 4. Generate embeddings via OpenAI
    # 5. Store in pgvector with Document/DocumentChunk
    
    return JsonResponse({
        'status': 'stub',
        'message': 'Document ingestion - implement in Fase B'
    })
