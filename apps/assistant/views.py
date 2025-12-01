"""
Views for Assistant (Helix Secretary) - FASE C (UI/HTMX + Ollama)

Integration:
- Chat endpoints with HTMX streaming responses
- RAG query processing using Ollama + pgvector
- Document management and ingestion
- Error handling and user feedback

Stack:
- Ollama (qwen2.5:14b LLM)
- Nomic Embed (embeddings)
- pgvector (similarity search)
- HTMX (frontend interactivity)
- Django templates (server-side rendering)
"""

import logging
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.views.decorators.http import require_http_methods, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import datetime

from .models import Conversation, Message, Document, DocumentChunk
from .services import (
    HelixAssistant, 
    DocumentIngestion, 
    RAGPipeline,
    check_ollama_connection,
    get_helix_status
)

logger = logging.getLogger(__name__)


# ===== Chat Endpoints (HTMX) =====

@login_required
@require_http_methods(["GET"])
def chat_interface(request):
    """
    Main chat interface page
    
    Displays:
    - Conversation list (sidebar)
    - Chat window (main)
    - Chat history
    
    Returns: Full HTML page
    """
    try:
        # Get user's conversations
        conversations = Conversation.objects.filter(
            user=request.user,
            company=request.user.tenant
        ).order_by('-created_at')
        
        # Get or create default conversation
        default_conv, _ = Conversation.objects.get_or_create(
            user=request.user,
            company=request.user.tenant,
            defaults={
                'title': f'Conversa iniciada em {now().strftime("%d/%m %H:%M")}'
            }
        )
        
        # Get history for default conversation
        history = HelixAssistant.get_conversation_history(default_conv, limit=20)
        
        context = {
            'conversations': conversations,
            'active_conversation': default_conv,
            'history': history,
            'helix_status': get_helix_status(),
        }
        return render(request, 'assistant/chat_interface.html', context)
        
    except Exception as e:
        logger.error(f"Error loading chat interface: {e}")
        return render(request, 'assistant/error.html', {'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def chat_message(request):
    """
    Handle incoming chat messages via HTMX
    
    Endpoint: POST /api/chat/message/
    
    Request:
    {
        "conversation_id": 123,
        "message": "O que é o sistema?"
    }
    
    Response: HTML fragment with assistant response + citations
    """
    try:
        # Parse request
        conversation_id = request.POST.get('conversation_id')
        user_message = request.POST.get('message', '').strip()
        
        if not user_message:
            return HttpResponse("Mensagem vazia", status=400)
        
        # Get conversation
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )
        
        logger.info(f"Chat message from {request.user}: {user_message[:50]}...")
        
        # Create user message record
        user_msg = Message.objects.create(
            conversation=conversation,
            role='user',
            content=user_message,
            context_sources=[],
        )
        
        # Generate assistant response
        response_data = HelixAssistant.chat(
            user_message=user_message,
            conversation=conversation,
            user_id=request.user.id,
        )
        
        # Render messages as HTML fragments
        context = {
            'user_message': user_message,
            'user_timestamp': user_msg.created_at.strftime("%H:%M"),
            'assistant_response': response_data['response'],
            'citations': response_data['citations'],
            'assistant_timestamp': now().strftime("%H:%M"),
            'status': response_data['status'],
        }
        
        html = render_to_string(
            'assistant/partials/messages.html',
            context
        )
        
        return HttpResponse(html)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        error_html = f"""
        <div class="bg-[#122E40] text-red-300 rounded p-3 text-sm">
            <strong>Erro:</strong> {str(e)}
        </div>
        """
        return HttpResponse(error_html, status=500)


@login_required
@require_http_methods(["GET"])
def chat_history(request, conversation_id):
    """
    Retrieve chat history for HTMX infinite scroll
    
    Endpoint: GET /assistant/history/<conversation_id>/
    
    Query params:
    - limit: Number of messages (default: 10)
    - offset: Pagination offset (default: 0)
    
    Returns: HTML fragment with message list
    """
    try:
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )
        
        limit = int(request.GET.get('limit', 10))
        offset = int(request.GET.get('offset', 0))
        
        # Get paginated messages
        messages = conversation.messages.all().order_by('-created_at')[offset:offset + limit]
        
        context = {
            'messages': reversed(list(messages)),
            'conversation': conversation,
        }
        
        html = render_to_string(
            'assistant/partials/history.html',
            context
        )
        
        return HttpResponse(html)
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return HttpResponse(f"Erro: {str(e)}", status=500)


@login_required
@require_http_methods(["POST"])
def create_conversation(request):
    """
    Create new conversation
    
    Endpoint: POST /api/chat/new/
    
    Returns: Redirect to new conversation
    """
    try:
        title = request.POST.get('title', f'Conversa de {now().strftime("%d/%m %H:%M")}')
        
        conversation = Conversation.objects.create(
            user=request.user,
            company=request.user.tenant,
            title=title,
            is_active=True,
        )
        
        logger.info(f"Created conversation {conversation.id}")
        
        # Redirect to chat interface with new conversation
        return redirect('assistant:chat_interface')
        
    except Exception as e:
        logger.error(f"Create conversation error: {e}")
        return HttpResponse(f"Erro: {str(e)}", status=500)


# ===== Document Management =====

@login_required
@require_http_methods(["GET"])
def list_documents(request):
    """
    List all documents in knowledge base
    
    Endpoint: GET /api/documents/
    
    Returns: JSON list of documents
    """
    try:
        documents = Document.objects.filter(
            company=request.user.tenant,
            is_active=True
        ).values(
            'id', 'title', 'source_path', 'content_type',
            'ingested_at', 'version'
        )
        
        # Count chunks per document
        docs_with_counts = []
        for doc in documents:
            chunk_count = DocumentChunk.objects.filter(
                document_id=doc['id']
            ).count()
            doc['chunk_count'] = chunk_count
            docs_with_counts.append(doc)
        
        return JsonResponse({
            'documents': list(docs_with_counts),
            'total': len(docs_with_counts),
        })
        
    except Exception as e:
        logger.error(f"List documents error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def ingest_documents(request):
    """
    Trigger document ingestion
    
    Endpoint: POST /api/documents/ingest/
    
    Process:
    1. Read docs/ folder
    2. Generate embeddings via Ollama
    3. Store in pgvector
    4. Return statistics
    
    Returns: JSON with ingestion results
    """
    try:
        logger.info(f"Starting document ingestion for company {request.user.tenant.id}")
        
        # Check Ollama connection
        if not check_ollama_connection():
            return JsonResponse({
                'status': 'error',
                'message': 'Ollama não está disponível. Inicie o serviço.'
            }, status=503)
        
        # Ingest documents
        result = DocumentIngestion.ingest_documents(
            company_id=request.user.tenant.id
        )
        
        logger.info(f"Ingestion complete: {result}")
        
        return JsonResponse({
            'status': result['status'],
            'documents_ingested': result.get('documents_ingested', 0),
            'chunks_created': result.get('chunks_created', 0),
            'errors': result.get('errors', 0),
            'message': result.get('message', 'Ingestion complete'),
        })
        
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ===== Health Check =====

@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint
    
    Returns: System status (Ollama, embeddings, database)
    """
    try:
        status = get_helix_status()
        return JsonResponse(status)
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# ===== Error Views =====

def assistant_error(request, exception=None):
    """Error page for assistant app"""
    return render(request, 'assistant/error.html', {
        'error': str(exception) if exception else 'Unknown error'
    }, status=500)
    
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
