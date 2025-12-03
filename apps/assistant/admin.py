"""
Helix Admin Dashboard - Advanced Admin Interface (FASE E+)

Features:
- Document management (upload, delete, reindex)
- Conversation analytics (users, messages, tokens)
- System monitoring (GPU, memory, response times)
- Configuration management (prompts, thresholds)
- User activity logs
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta

from .models import Document, DocumentChunk, Conversation, Message, HelixConfig
from .services import get_helix_status
from .gpu_manager import GPUManager


class HelixAdminSite(AdminSite):
    """Custom admin site for Helix"""
    site_header = "Assistente Helix - Admin"
    site_title = "Helix Admin"
    index_title = "Dashboard"
    
    def index(self, request):
        """Custom dashboard index"""
        from django.template.response import TemplateResponse
        
        # Get analytics
        total_conversations = Conversation.objects.count()
        total_messages = Message.objects.count()
        total_documents = Document.objects.count()
        total_chunks = DocumentChunk.objects.count()
        
        # Get user stats
        from apps.core.models import Company
        total_users = Company.objects.count()
        
        # Get system status
        try:
            system_status = get_helix_status()
            gpu_info = GPUManager.get_performance_metrics()
        except Exception:
            system_status = {}
            gpu_info = {}
        
        # Get recent activity
        recent_conversations = Conversation.objects.select_related('user', 'company').order_by('-created_at')[:5]
        recent_messages = Message.objects.select_related('conversation').order_by('-created_at')[:10]
        
        # Get analytics
        messages_7d = Message.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        conversations_7d = Conversation.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        context = {
            'title': 'Helix Dashboard',
            'stats': {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'total_documents': total_documents,
                'total_chunks': total_chunks,
                'total_users': total_users,
                'messages_7d': messages_7d,
                'conversations_7d': conversations_7d,
            },
            'system_status': system_status,
            'gpu_info': gpu_info,
            'recent_conversations': recent_conversations,
            'recent_messages': recent_messages,
        }
        
        return TemplateResponse(request, 'admin/helix_dashboard.html', context)


helix_admin = HelixAdminSite(name='helix_admin')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for Document model - ENHANCED"""
    
    list_display = ['title', 'company_name', 'content_type', 'chunk_count', 'ingested_at', 'status_badge']
    list_filter = ['company', 'is_active', 'content_type', 'ingested_at']
    search_fields = ['title', 'source_path', 'content']
    readonly_fields = ['ingested_at', 'updated_at', 'created_at', 'chunk_count_display']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'source_path', 'company')
        }),
        ('Content', {
            'fields': ('content', 'content_type')
        }),
        ('Metadata', {
            'fields': ('version', 'is_active', 'ingested_at', 'updated_at', 'chunk_count_display')
        }),
    )
    
    def company_name(self, obj):
        return obj.company.name if obj.company else '-'
    company_name.short_description = 'Company'
    
    def chunk_count(self, obj):
        return obj.documentchunk_set.count()
    chunk_count.short_description = 'Chunks'
    
    def chunk_count_display(self, obj):
        return obj.documentchunk_set.count()
    chunk_count_display.short_description = 'Total Chunks'
    
    def status_badge(self, obj):
        color = 'green' if obj.is_active else 'red'
        status = 'Active' if obj.is_active else 'Inactive'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'




@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    """Admin interface for DocumentChunk model"""
    
    list_display = ['document_title', 'chunk_index', 'content_preview', 'created_at']
    list_filter = ['document__company', 'created_at', 'document']
    search_fields = ['document__title', 'content']
    readonly_fields = ['created_at', 'embedding_info']
    
    fieldsets = (
        ('Document Reference', {
            'fields': ('document', 'chunk_index')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Embedding', {
            'fields': ('embedding_info',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def document_title(self, obj):
        return obj.document.title if obj.document else '-'
    document_title.short_description = 'Document'
    
    def content_preview(self, obj):
        preview = obj.content[:50] if obj.content else '-'
        return f"{preview}..." if len(obj.content or '') > 50 else preview
    content_preview.short_description = 'Content Preview'
    
    def embedding_info(self, obj):
        if obj.embedding:
            embedding_size = len(obj.embedding)
            return f"Vector dimension: {embedding_size}"
        return "No embedding"
    embedding_info.short_description = 'Embedding Info'


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
