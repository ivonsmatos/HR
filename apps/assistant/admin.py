"""Assistant app admin configuration."""
from django.contrib import admin
from .models import Document, DocumentChunk, Conversation, Message, HelixConfig
from .services import get_helix_status


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "content_type", "version", "is_active", "ingested_at")
    list_filter = ("company", "content_type", "is_active", "ingested_at")
    search_fields = ("title", "source_path", "content")
    readonly_fields = ("ingested_at", "updated_at")


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ("document", "chunk_index", "token_count", "embedding_model")
    list_filter = ("document__company", "embedding_model")
    search_fields = ("content", "document__title")
    readonly_fields = ("embedding", "created_at", "updated_at")


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "content", "context_sources", "created_at")
    can_delete = False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "company", "is_active", "created_at")
    list_filter = ("company", "is_active", "created_at")
    search_fields = ("title", "user__username", "user__email")
    inlines = [MessageInline]
    readonly_fields = ("created_at",)


@admin.register(HelixConfig)
class HelixConfigAdmin(admin.ModelAdmin):
    list_display = ("company", "is_enabled", "max_context_chunks", "temperature")
    list_filter = ("is_enabled",)
    search_fields = ("company__name",)
    
    change_list_template = "admin/helix_change_list.html"
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['helix_status'] = get_helix_status()
        return super().changelist_view(request, extra_context=extra_context)
