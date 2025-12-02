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
        help_text="Document title (e.g., 'Installation Guide')"
    )
    source_path = models.CharField(
        max_length=500,
        help_text="Original file path (e.g., 'docs/setup.md')"
    )
    content = models.TextField(
        help_text="Full document content"
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
        help_text="Document version"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Include in RAG knowledge base"
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
        help_text="Sequential chunk number within document"
    )
    content = models.TextField(
        help_text="Text content of this chunk"
    )
    
    # Vector embedding (pgvector - 1536 dimensions for text-embedding-3-small)
    embedding = ArrayField(
        models.FloatField(),
        size=1536,
        null=True,
        blank=True,
        help_text="OpenAI embedding vector (1536 dimensions for text-embedding-3-small)"
    )
    
    # Embedding metadata
    token_count = models.IntegerField(
        default=0,
        help_text="Token count for this chunk"
    )
    embedding_model = models.CharField(
        max_length=100,
        default='text-embedding-3-small',
        help_text="OpenAI model used for embedding"
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
        help_text="Auto-generated conversation title"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Mark as archived"
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
        help_text="Who sent the message"
    )
    
    content = models.TextField(
        help_text="Message content"
    )
    
    # Context for assistant responses
    context_sources = models.JSONField(
        default=list,
        blank=True,
        help_text="Documents/chunks used for response (RAG context)"
    )
    
    # Metadata
    tokens_used = models.IntegerField(
        default=0,
        help_text="OpenAI tokens consumed by this message"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
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
        help_text="Enable Helix for this company"
    )
    
    # System prompt customization
    system_prompt = models.TextField(
        default="Você é o Secretário Virtual do sistema Onyx Helix. Responda de forma concisa, profissional e sempre baseando-se estritamente no contexto fornecido. Se não souber a resposta, diga que precisa de ajuda de um humano.",
        help_text="System prompt for LLM (Portuguese)"
    )
    
    # Response parameters
    max_context_chunks = models.IntegerField(
        default=5,
        help_text="Maximum number of document chunks to use as context"
    )
    temperature = models.FloatField(
        default=0.3,
        help_text="LLM temperature (0.0 to 1.0)"
    )
    
    # Advanced settings
    enable_citation = models.BooleanField(
        default=True,
        help_text="Include source citations in responses"
    )
    
    similarity_threshold = models.FloatField(
        default=0.7,
        help_text="Minimum similarity score for relevant chunks (0.0 to 1.0)"
    )
    
    class Meta:
        verbose_name = "Helix Configuration"
        verbose_name_plural = "Helix Configurations"
        unique_together = ['company']
    
    def __str__(self):
        return f"Helix Config - {self.company.name}"
