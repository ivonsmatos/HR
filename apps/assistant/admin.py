"""
Admin interface for Assistant app
"""

from django.contrib import admin
from .models import Document, DocumentChunk, Conversation, Message, HelixConfig


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model"""
    
    list_display = ['title', 'source_path', 'company', 'is_active', 'ingested_at']
    list_filter = ['company', 'is_active', 'content_type', 'ingested_at']
    search_fields = ['title', 'source_path', 'content']
    readonly_fields = ['ingested_at', 'updated_at', 'created_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'source_path', 'company')
        }),
        ('Content', {
            'fields': ('content', 'content_type')
        }),
        ('Metadata', {
            'fields': ('version', 'is_active', 'ingested_at', 'updated_at')
        }),
        ('Audit', {
            'fields': ('created_by', 'updated_by', 'created_at')
        }),
    )


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    """Admin interface for DocumentChunk model"""
    
    list_display = ['document', 'chunk_index', 'token_count', 'embedding_model', 'created_at']
    list_filter = ['document__company', 'embedding_model', 'created_at']
    search_fields = ['document__title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Document Reference', {
            'fields': ('document', 'chunk_index')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Embedding', {
            'fields': ('token_count', 'embedding_model')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model"""
    
    list_display = ['user', 'title', 'company', 'is_active', 'created_at', 'message_count']
    list_filter = ['company', 'is_active', 'created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Conversation Info', {
            'fields': ('user', 'company', 'title')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
    
    def message_count(self, obj):
        """Display message count"""
        return obj.messages.count()
    
    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model"""
    
    list_display = ['conversation', 'role', 'content_preview', 'tokens_used', 'created_at']
    list_filter = ['conversation__company', 'role', 'created_at']
    search_fields = ['conversation__user__username', 'content']
    readonly_fields = ['created_at', 'updated_at', 'context_sources']
    
    fieldsets = (
        ('Message Info', {
            'fields': ('conversation', 'role')
        }),
        ('Content', {
            'fields': ('content', 'context_sources')
        }),
        ('Metadata', {
            'fields': ('tokens_used', 'created_at', 'updated_at')
        }),
    )
    
    def content_preview(self, obj):
        """Show content preview"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    
    content_preview.short_description = "Content"


@admin.register(HelixConfig)
class HelixConfigAdmin(admin.ModelAdmin):
    """Admin interface for HelixConfig model"""
    
    list_display = ['company', 'is_enabled', 'temperature', 'max_context_chunks']
    list_filter = ['company', 'is_enabled']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Configuration', {
            'fields': ('company', 'is_enabled')
        }),
        ('System Prompt', {
            'fields': ('system_prompt',),
            'classes': ('collapse',)
        }),
        ('Response Settings', {
            'fields': ('temperature', 'max_context_chunks', 'similarity_threshold')
        }),
        ('Features', {
            'fields': ('enable_citation',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
