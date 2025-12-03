"""
Painel SyncRH - Interface Avançada de Administração (FASE E+)

Recursos:
- Gestão de documentos (upload, deletar, reindexar)
- Análise de conversas (usuários, mensagens, tokens)
- Monitoramento do sistema (GPU, memória, tempos de resposta)
- Gestão de configuração (prompts, limites)
- Logs de atividade do usuário
"""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.utils import timezone
from datetime import timedelta

from .models import Documento, DocumentoChunk, Conversa, Mensagem, HelixConfig
from .services import get_helix_status
from .gpu_manager import GPUManager


class HelixAdminSite(AdminSite):
    """Site de administração personalizado para SyncRH"""
    site_header = "Assistente SyncRH - Admin"
    site_title = "Admin SyncRH"
    index_title = "Painel"
    
    def index(self, request):
        """Índice personalizado do painel"""
        from django.template.response import TemplateResponse
        
        # Obter análises
        total_conversations = Conversa.objects.count()
        total_messages = Mensagem.objects.count()
        total_documents = Documento.objects.count()
        total_chunks = DocumentoChunk.objects.count()
        
        # Obter estatísticas de usuário
        from apps.core.models import Empresa
        total_users = Empresa.objects.count()
        
        # Obter status do sistema
        try:
            system_status = get_helix_status()
            gpu_info = GPUManager.get_performance_metrics()
        except Exception:
            system_status = {}
            gpu_info = {}
        
        # Obter atividade recente
        recent_conversations = Conversa.objects.select_related('user', 'company').order_by('-created_at')[:5]
        recent_messages = Mensagem.objects.select_related('conversation').order_by('-created_at')[:10]
        
        # Obter análises
        messages_7d = Mensagem.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        conversations_7d = Conversa.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        context = {
            'title': 'Painel SyncRH',
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
        
        return TemplateResponse(request, 'admin/syncrh_dashboard.html', context)


helix_admin = HelixAdminSite(name='helix_admin')


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    """Interface de administração para o modelo Documento - APRIMORADO"""
    
    list_display = ['title', 'company_name', 'content_type', 'chunk_count', 'ingested_at', 'status_badge']
    list_filter = ['company', 'is_active', 'content_type', 'ingested_at']
    search_fields = ['title', 'source_path', 'content']
    readonly_fields = ['ingested_at', 'updated_at', 'created_at', 'chunk_count_display']
    
    fieldsets = (
        ('Informaçãormações Básicas', {
            'fields': ('title', 'source_path', 'company')
        }),
        ('Conteúdo', {
            'fields': ('content', 'content_type')
        }),
        ('Metadados', {
            'fields': ('version', 'is_active', 'ingested_at', 'updated_at', 'chunk_count_display')
        }),
    )
    
    def company_name(self, obj):
        return obj.company.name if obj.company else '-'
    company_name.short_description = 'Empresa'
    
    def chunk_count(self, obj):
        return obj.documentchunk_set.count()
    chunk_count.short_description = 'Fragmentos'
    
    def chunk_count_display(self, obj):
        return obj.documentchunk_set.count()
    chunk_count_display.short_description = 'Total Chunks'
    
    def status_badge(self, obj):
        color = 'green' if obj.is_active else 'red'
        status = 'Ativo' if obj.is_active else 'Inativo'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            status
        )
    status_badge.short_description = 'Status'




@admin.register(DocumentoChunk)
class DocumentoChunkAdmin(admin.ModelAdmin):
    """Interface de administração para o modelo DocumentoChunk"""
    
    list_display = ['document_title', 'chunk_index', 'content_preview', 'created_at']
    list_filter = ['document__company', 'created_at', 'document']
    search_fields = ['document__title', 'content']
    readonly_fields = ['created_at', 'embedding_info']
    
    fieldsets = (
        ('Referência do Documentoo', {
            'fields': ('document', 'chunk_index')
        }),
        ('Conteúdo', {
            'fields': ('content',)
        }),
        ('Incorporação', {
            'fields': ('embedding_info',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def document_title(self, obj):
        return obj.document.title if obj.document else '-'
    document_title.short_description = 'Documentoo'
    
    def content_preview(self, obj):
        preview = obj.content[:50] if obj.content else '-'
        return f"{preview}..." if len(obj.content or '') > 50 else preview
    content_preview.short_description = 'Prévia do Conteúdo'
    
    def embedding_info(self, obj):
        if obj.embedding:
            embedding_size = len(obj.embedding)
            return f"Dimensão do vetor: {embedding_size}"
        return "Sem incorporação"
    embedding_info.short_description = 'Informaçãormações de Incorporação'


@admin.register(Conversa)
class ConversaAdmin(admin.ModelAdmin):
    """Interface de administração para o modelo Conversa"""
    
    list_display = ['user', 'title', 'company', 'is_active', 'created_at', 'message_count']
    list_filter = ['company', 'is_active', 'created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Informaçãormações da Conversa', {
            'fields': ('user', 'company', 'title')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Auditoriaoria', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
    
    def message_count(self, obj):
        """Exibir contagem de mensagens"""
        return obj.messages.count()
    
    message_count.short_description = "Mensagens"


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    """Interface de administração para o modelo Mensagem"""
    
    list_display = ['conversation', 'role', 'content_preview', 'tokens_used', 'created_at']
    list_filter = ['conversation__company', 'role', 'created_at']
    search_fields = ['conversation__user__username', 'content']
    readonly_fields = ['created_at', 'updated_at', 'context_sources']
    
    fieldsets = (
        ('Informaçãormações da Mensagem', {
            'fields': ('conversation', 'role')
        }),
        ('Conteúdo', {
            'fields': ('content', 'context_sources')
        }),
        ('Metadados', {
            'fields': ('tokens_used', 'created_at', 'updated_at')
        }),
    )
    
    def content_preview(self, obj):
        """Mostrar prévia do conteúdo"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    
    content_preview.short_description = "Conteúdo"


@admin.register(HelixConfig)
class HelixConfigAdmin(admin.ModelAdmin):
    """Interface de administração para o modelo HelixConfig"""
    
    list_display = ['company', 'is_enabled', 'temperature', 'max_context_chunks']
    list_filter = ['company', 'is_enabled']
    readonly_fields = ['created_at', 'updated_at', 'created_by', 'updated_by']
    
    fieldsets = (
        ('Configuração', {
            'fields': ('company', 'is_enabled')
        }),
        ('Prompt do Sistema', {
            'fields': ('system_prompt',),
            'classes': ('collapse',)
        }),
        ('Configurações de Resposta', {
            'fields': ('temperature', 'max_context_chunks', 'similarity_threshold')
        }),
        ('Recursos', {
            'fields': ('enable_citation',)
        }),
        ('Auditoriaoria', {
            'fields': ('created_at', 'updated_at', 'created_by', 'updated_by')
        }),
    )
