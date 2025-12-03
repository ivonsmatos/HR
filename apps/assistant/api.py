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
from django_filters.rest_framework import DjangoFiltrarVoltarend
from rest_framework.filters import PesquisarFiltrar, OrderingFiltrar

from .models import Documento, DocumentoChunk, Conversa, Mensagem
from .services import HelixAssistant, DocumentoIngestion, RAGPipeline


# ===== Serializers =====

class DocumentoSerializer(serializers.ModelSerializer):
    """Serialize Documento model"""
    
    chunks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Documento
        fields = [
            'id', 'title', 'source_path', 'content_type',
            'ingested_at', 'version', 'is_active', 'chunks_count'
        ]
        read_only_fields = ['id', 'ingested_at', 'chunks_count']
    
    def get_chunks_count(self, obj):
        return obj.documentchunk_set.count()


class DocumentoChunkSerializer(serializers.ModelSerializer):
    """Serialize DocumentoChunk model"""
    
    document_title = serializers.CharField(
        source='document.title',
        read_only=True
    )
    
    class Meta:
        model = DocumentoChunk
        fields = [
            'id', 'document_title', 'chunk_index', 'content',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MensagemSerializer(serializers.ModelSerializer):
    """Serialize Mensagem model"""
    
    class Meta:
        model = Mensagem
        fields = [
            'id', 'role', 'content', 'context_sources',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ConversaSerializer(serializers.ModelSerializer):
    """Serialize Conversa model"""
    
    messages = MensagemSerializer(
        source='message_set',
        many=True,
        read_only=True
    )
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversa
        fields = [
            'id', 'title', 'created_at', 'is_active',
            'message_count', 'messages'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_message_count(self, obj):
        return obj.message_set.count()


class ChatMensagemSerializer(serializers.Serializer):
    """Serialize chat message request/response"""
    
    conversation_id = serializers.IntegerField()
    message = serializers.CharField()
    
    class ResponseSerializer(serializers.Serializer):
        response = serializers.CharField()
        citations = serializers.ListField(child=serializers.DictField())
        status = serializers.CharField()
        message_id = serializers.IntegerField()


# ===== ViewSets =====

class DocumentoViewSet(viewsets.ModelViewSet):
    """ViewSet for Documento management"""
    
    serializer_class = DocumentoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFiltrarVoltarend, PesquisarFiltrar, OrderingFiltrar]
    filterset_fields = ['company', 'content_type', 'is_active']
    search_fields = ['title', 'source_path']
    ordering_fields = ['ingested_at', 'title']
    ordering = ['-ingested_at']
    
    def get_queryset(self):
        """Filtrar by user's company"""
        return Documento.objects.filter(
            company=self.request.user.tenant
        )
    
    @action(detail=False, methods=['post'])
    def ingest(self, request):
        """Trigger document ingestion"""
        result = DocumentoIngestion.ingest_documents(
            company_id=request.user.tenant.id
        )
        return Response(result)


class DocumentoChunkViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for DocumentoChunk (read-only)"""
    
    serializer_class = DocumentoChunkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFiltrarVoltarend, PesquisarFiltrar]
    filterset_fields = ['document']
    search_fields = ['content']
    
    def get_queryset(self):
        """Filtrar by user's company"""
        return DocumentoChunk.objects.filter(
            document__company=self.request.user.tenant
        )


class ConversaViewSet(viewsets.ModelViewSet):
    """ViewSet for Conversa management"""
    
    serializer_class = ConversaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFiltrarVoltarend, OrderingFiltrar]
    filterset_fields = ['is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtrar by current user"""
        return Conversa.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create conversation for current user"""
        serializer.save(
            user=self.request.user,
            company=self.request.user.tenant
        )


class MensagemViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Mensagem (read-only)"""
    
    serializer_class = MensagemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFiltrarVoltarend]
    filterset_fields = ['conversation', 'role']
    
    def get_queryset(self):
        """Filtrar by user's conversations"""
        return Mensagem.objects.filter(
            conversation__user=self.request.user
        )
    
    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """Send message and get AI response"""
        serializer = ChatMensagemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conversation_id = serializer.validated_data['conversation_id']
        message_text = serializer.validated_data['message']
        
        # Get conversation
        try:
            conversation = Conversa.objects.get(
                id=conversation_id,
                user=request.user
            )
        except Conversa.DoesNãotExist:
            return Response(
                {'error': 'Conversa not found'},
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
            'message_id': last_message.id if last_message else Nãone,
        })


# ===== GraphQL Schema (using Graphene) =====

try:
    import graphene
    from graphene_django import DjangoObjectType
    
    class DocumentoType(DjangoObjectType):
        chunks_count = graphene.Int()
        
        class Meta:
            model = Documento
            fields = [
                'id', 'title', 'source_path', 'content_type',
                'ingested_at', 'is_active'
            ]
        
        def resolve_chunks_count(self, info):
            return self.documentchunk_set.count()
    
    
    class DocumentoChunkType(DjangoObjectType):
        class Meta:
            model = DocumentoChunk
            fields = ['id', 'document', 'chunk_index', 'content', 'created_at']
    
    
    class MensagemType(DjangoObjectType):
        class Meta:
            model = Mensagem
            fields = ['id', 'role', 'content', 'created_at']
    
    
    class ConversaType(DjangoObjectType):
        message_count = graphene.Int()
        
        class Meta:
            model = Conversa
            fields = ['id', 'title', 'created_at', 'is_active']
        
        def resolve_message_count(self, info):
            return self.message_set.count()
    
    
    class Query(graphene.ObjectType):
        """GraphQL Query root"""
        
        documents = graphene.List(DocumentoType)
        document = graphene.Field(DocumentoType, id=graphene.Int(required=True))
        
        conversations = graphene.List(ConversaType)
        conversation = graphene.Field(ConversaType, id=graphene.Int(required=True))
        
        def resolve_documents(self, info):
            if not info.context.user.is_authenticated:
                return Documento.objects.none()
            return Documento.objects.filter(company=info.context.user.tenant)
        
        def resolve_document(self, info, id):
            if not info.context.user.is_authenticated:
                return Nãone
            try:
                return Documento.objects.get(id=id, company=info.context.user.tenant)
            except Documento.DoesNãotExist:
                return Nãone
        
        def resolve_conversations(self, info):
            if not info.context.user.is_authenticated:
                return Conversa.objects.none()
            return Conversa.objects.filter(user=info.context.user)
        
        def resolve_conversation(self, info, id):
            if not info.context.user.is_authenticated:
                return Nãone
            try:
                return Conversa.objects.get(id=id, user=info.context.user)
            except Conversa.DoesNãotExist:
                return Nãone
    
    
    class SendMensagemMutation(graphene.Mutation):
        """Send message mutation"""
        
        class Arguments:
            conversation_id = graphene.Int(required=True)
            message = graphene.String(required=True)
        
        response = graphene.String()
        citations = graphene.List(graphene.JSONString)
        status = graphene.String()
        
        def mutate(self, info, conversation_id, message):
            if not info.context.user.is_authenticated:
                raise Exception("Usuário not authenticated")
            
            try:
                conversation = Conversa.objects.get(
                    id=conversation_id,
                    user=info.context.user
                )
            except Conversa.DoesNãotExist:
                raise Exception("Conversa not found")
            
            response_data = HelixAssistant.chat(
                user_message=message,
                conversation=conversation,
                user_id=info.context.user.id
            )
            
            return SendMensagemMutation(
                response=response_data['response'],
                citations=response_data['citations'],
                status=response_data['status']
            )
    
    
    class Mutation(graphene.ObjectType):
        send_message = SendMensagemMutation.Field()
    
    
    # Create schema
    schema = graphene.Schema(query=Query, mutation=Mutation)
    
except ImportarErro:
    schema = Nãone

