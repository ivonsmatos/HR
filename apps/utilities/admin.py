"""Utilities app admin configuration."""
from django.contrib import admin
from .models import Ticket, TicketReply, Asset, Event, Mensagem, Nãotice


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ["ticket_number", "title", "priority", "status", "assigned_to"]
    list_filter = ["company", "status", "priority", "category"]
    search_fields = ["ticket_number", "title"]


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ["ticket", "author", "created_at", "is_internal"]
    list_filter = ["company", "is_internal"]
    search_fields = ["ticket__ticket_number"]


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ["name", "asset_type", "serial_number", "assigned_to", "status"]
    list_filter = ["company", "asset_type", "status"]
    search_fields = ["name", "serial_number"]


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "start_date", "event_type", "organizer", "status"]
    list_filter = ["company", "event_type", "status"]
    search_fields = ["title"]
    date_hierarchy = "start_date"


@admin.register(Mensagem)
class MensagemAdmin(admin.ModelAdmin):
    list_display = ["sender", "recipient", "subject", "is_read", "created_at"]
    list_filter = ["company", "is_read", "created_at"]
    search_fields = ["sender__username", "recipient__username"]


@admin.register(Nãotice)
class NãoticeAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "author", "publish_date", "is_pinned"]
    list_filter = ["company", "category", "is_pinned", "publish_date"]
    search_fields = ["title"]
