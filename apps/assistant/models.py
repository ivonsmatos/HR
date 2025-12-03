"""
Models for Assistant (Helix Secretary)
Stores conversation history and document metadata
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.core.models import Company, TenantAwareModel, User
import uuid


class Document(TenantAwareModel):
    """
    Represents a document ingested for RAG
    Stores metadata about source files and chunks
    """
    
    title = models.CharField(
        max_length=255,
        help_text="Título do documento (ex: 'Guia de Instalação')"
    )
    source_path = models.CharField(
        max_length=500,
        help_text="Caminho original do arquivo (ex: 'docs/setup.md')"
    )
    content = models.TextField(
        help_text="Conteúdo completo do documento"
    )
    content_type = models.CharField(
        max_length=50,
        choices=[
            ('markdown', 'Markdown'),
            ('text', 'Plain Text'),
            ('html', 'HTML'),
        ],
        default='markdown'
    )
    
    # Metadata
    version = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Versão do documento"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Incluir na base de conhecimento RAG"
    )
    ingested_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-ingested_at']
        indexes = [
            models.Index(fields=['company', 'is_active']),
            models.Index(fields=['source_path']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.company.slug})"


class DocumentChunk(models.Model):
    """
    Vector chunk of a document
    Stores embeddings in pgvector column
    """
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks'
    )
    
    chunk_index = models.IntegerField(
        help_text="Número sequencial do chunk dentro do documento"
    )
    content = models.TextField(
        help_text="Conteúdo de texto deste chunk"
    )
    
    # Vector embedding (pgvector - 1536 dimensions for text-embedding-3-small)
    embedding = ArrayField(
        models.FloatField(),
        size=1536,
        null=True,
        blank=True,
        help_text="Vetor de embedding da OpenAI (1536 dimensões para text-embedding-3-small)"
    )
    
    # Embedding metadata
    token_count = models.IntegerField(
        default=0,
        help_text="Contagem de tokens para este chunk"
    )
    embedding_model = models.CharField(
        max_length=100,
        default='text-embedding-3-small',
        help_text="Modelo OpenAI usado para embedding"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Document Chunk"
        verbose_name_plural = "Document Chunks"
        ordering = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
        unique_together = ['document', 'chunk_index']
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class Conversation(TenantAwareModel):
    """
    Stores conversation history with Helix Secretary
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assistant_conversations'
    )
    
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Título da conversa gerado automaticamente"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Marcar como arquivado"
    )
    
    class Meta:
        verbose_name = "Conversation"
        verbose_name_plural = "Conversations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'company', '-created_at']),
        ]
    
    def __str__(self):
        return f"Chat with {self.user.username} ({self.company.slug})"


class Message(models.Model):
    """
    Individual message in a conversation
    """
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant (Helix)'),
        ('system', 'System'),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        help_text="Quem enviou a mensagem"
    )
    
    content = models.TextField(
        help_text="Conteúdo da mensagem"
    )
    
    # Context for assistant responses
    context_sources = models.JSONField(
        default=list,
        blank=True,
        help_text="Documentos/chunks usados para resposta (contexto RAG)"
    )
    
    # Metadata
    tokens_used = models.IntegerField(
        default=0,
        help_text="Tokens OpenAI consumidos por esta mensagem"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return f"{self.role.upper()}: {self.content[:50]}..."


class HelixConfig(TenantAwareModel):
    """
    Configuration per tenant for Helix Secretary
    """
    
    # Enable/Disable per company
    is_enabled = models.BooleanField(
        default=True,
        help_text="Ativar Helix para esta empresa"
    )
    
    # System prompt customization
    system_prompt = models.TextField(
        default="Você é o Secretário Virtual do sistema Onyx Helix. Responda de forma concisa, profissional e sempre baseando-se estritamente no contexto fornecido. Se não souber a resposta, diga que precisa de ajuda de um humano.",
        help_text="Prompt de sistema para LLM (Português)"
    )
    
    # Response parameters
    max_context_chunks = models.IntegerField(
        default=5,
        help_text="Número máximo de chunks de documento para usar como contexto"
    )
    temperature = models.FloatField(
        default=0.3,
        help_text="Temperatura do LLM (0,0 a 1,0)"
    )
    
    # Advanced settings
    enable_citation = models.BooleanField(
        default=True,
        help_text="Incluir citações de fonte nas respostas"
    )
    
    similarity_threshold = models.FloatField(
        default=0.7,
        help_text="Escore mínimo de similaridade para chunks relevantes (0,0 a 1,0)"
    )
    
    class Meta:
        verbose_name = "Helix Configuration"
        verbose_name_plural = "Helix Configurations"
        unique_together = ['company']
    
    def __str__(self):
        return f"Helix Config - {self.company.name}"
