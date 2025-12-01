"""
Public API for Helix Assistant (FASE E+)

REST + GraphQL API for external integrations

Endpoints:
- GET /api/helix/documents/ - List documents
- POST /api/helix/documents/ - Create document
- POST /api/helix/chat/ - Send message
- GET /api/helix/conversations/ - List conversations
"""

from rest_framework import serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Document, DocumentChunk, Conversation, Message
from .services import HelixAssistant, DocumentIngestion, RAGPipeline


# ===== Serializers =====

class DocumentSerializer(serializers.ModelSerializer):
    """Serialize Document model"""
    
    chunks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'source_path', 'content_type',
            'ingested_at', 'version', 'is_active', 'chunks_count'
        ]
        read_only_fields = ['id', 'ingested_at', 'chunks_count']
    
    def get_chunks_count(self, obj):
        return obj.documentchunk_set.count()


class DocumentChunkSerializer(serializers.ModelSerializer):
    """Serialize DocumentChunk model"""
    
    document_title = serializers.CharField(
        source='document.title',
        read_only=True
    )
    
    class Meta:
        model = DocumentChunk
        fields = [
            'id', 'document_title', 'chunk_index', 'content',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serialize Message model"""
    
    class Meta:
        model = Message
        fields = [
            'id', 'role', 'content', 'context_sources',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    """Serialize Conversation model"""
    
    messages = MessageSerializer(
        source='message_set',
        many=True,
        read_only=True
    )
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'created_at', 'is_active',
            'message_count', 'messages'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_message_count(self, obj):
        return obj.message_set.count()


class ChatMessageSerializer(serializers.Serializer):
    """Serialize chat message request/response"""
    
    conversation_id = serializers.IntegerField()
    message = serializers.CharField()
    
    class ResponseSerializer(serializers.Serializer):
        response = serializers.CharField()
        citations = serializers.ListField(child=serializers.DictField())
        status = serializers.CharField()
        message_id = serializers.IntegerField()


# ===== ViewSets =====

class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for Document management"""
    
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['company', 'content_type', 'is_active']
    search_fields = ['title', 'source_path']
    ordering_fields = ['ingested_at', 'title']
    ordering = ['-ingested_at']
    
    def get_queryset(self):
        """Filter by user's company"""
        return Document.objects.filter(
            company=self.request.user.tenant
        )
    
    @action(detail=False, methods=['post'])
    def ingest(self, request):
        """Trigger document ingestion"""
        result = DocumentIngestion.ingest_documents(
            company_id=request.user.tenant.id
        )
        return Response(result)


class DocumentChunkViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DocumentChunk (read-only)"""
    
    serializer_class = DocumentChunkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['document']
    search_fields = ['content']
    
    def get_queryset(self):
        """Filter by user's company"""
        return DocumentChunk.objects.filter(
            document__company=self.request.user.tenant
        )


class ConversationViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversation management"""
    
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by current user"""
        return Conversation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create conversation for current user"""
        serializer.save(
            user=self.request.user,
            company=self.request.user.tenant
        )


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Message (read-only)"""
    
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['conversation', 'role']
    
    def get_queryset(self):
        """Filter by user's conversations"""
        return Message.objects.filter(
            conversation__user=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send message and get AI response"""
        serializer = ChatMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = serializer.validated_data['conversation_id']
        message_text = serializer.validated_data['message']
        
        # Get conversation
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                user=request.user
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate response
        response_data = HelixAssistant.chat(
            user_message=message_text,
            conversation=conversation,
            user_id=request.user.id
        )
        
        # Get last message ID
        last_message = conversation.message_set.order_by('-created_at').first()
        
        return Response({
            'response': response_data['response'],
            'citations': response_data['citations'],
            'status': response_data['status'],
            'message_id': last_message.id if last_message else None,
        })


# ===== GraphQL Schema (using Graphene) =====

try:
    import graphene
    from graphene_django import DjangoObjectType
    
    class DocumentType(DjangoObjectType):
        chunks_count = graphene.Int()
        
        class Meta:
            model = Document
            fields = [
                'id', 'title', 'source_path', 'content_type',
                'ingested_at', 'is_active'
            ]
        
        def resolve_chunks_count(self, info):
            return self.documentchunk_set.count()
    
    
    class DocumentChunkType(DjangoObjectType):
        class Meta:
            model = DocumentChunk
            fields = ['id', 'document', 'chunk_index', 'content', 'created_at']
    
    
    class MessageType(DjangoObjectType):
        class Meta:
            model = Message
            fields = ['id', 'role', 'content', 'created_at']
    
    
    class ConversationType(DjangoObjectType):
        message_count = graphene.Int()
        
        class Meta:
            model = Conversation
            fields = ['id', 'title', 'created_at', 'is_active']
        
        def resolve_message_count(self, info):
            return self.message_set.count()
    
    
    class Query(graphene.ObjectType):
        """GraphQL Query root"""
        
        documents = graphene.List(DocumentType)
        document = graphene.Field(DocumentType, id=graphene.Int(required=True))
        
        conversations = graphene.List(ConversationType)
        conversation = graphene.Field(ConversationType, id=graphene.Int(required=True))
        
        def resolve_documents(self, info):
            if not info.context.user.is_authenticated:
                return Document.objects.none()
            return Document.objects.filter(company=info.context.user.tenant)
        
        def resolve_document(self, info, id):
            if not info.context.user.is_authenticated:
                return None
            try:
                return Document.objects.get(id=id, company=info.context.user.tenant)
            except Document.DoesNotExist:
                return None
        
        def resolve_conversations(self, info):
            if not info.context.user.is_authenticated:
                return Conversation.objects.none()
            return Conversation.objects.filter(user=info.context.user)
        
        def resolve_conversation(self, info, id):
            if not info.context.user.is_authenticated:
                return None
            try:
                return Conversation.objects.get(id=id, user=info.context.user)
            except Conversation.DoesNotExist:
                return None
    
    
    class SendMessageMutation(graphene.Mutation):
        """Send message mutation"""
        
        class Arguments:
            conversation_id = graphene.Int(required=True)
            message = graphene.String(required=True)
        
        response = graphene.String()
        citations = graphene.List(graphene.JSONString)
        status = graphene.String()
        
        def mutate(self, info, conversation_id, message):
            if not info.context.user.is_authenticated:
                raise Exception("User not authenticated")
            
            try:
                conversation = Conversation.objects.get(
                    id=conversation_id,
                    user=info.context.user
                )
            except Conversation.DoesNotExist:
                raise Exception("Conversation not found")
            
            response_data = HelixAssistant.chat(
                user_message=message,
                conversation=conversation,
                user_id=info.context.user.id
            )
            
            return SendMessageMutation(
                response=response_data['response'],
                citations=response_data['citations'],
                status=response_data['status']
            )
    
    
    class Mutation(graphene.ObjectType):
        send_message = SendMessageMutation.Field()
    
    
    # Create schema
    schema = graphene.Schema(query=Query, mutation=Mutation)
    
except ImportError:
    schema = None

