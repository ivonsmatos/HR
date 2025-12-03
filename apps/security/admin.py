"""Security app admin configuration."""
from django.contrib import admin
from .models import IpBlocklist, TwoFactorAuth, UsuárioSession, SecurityEvent, AuditoriaConfig


@admin.register(IpBlocklist)
class IpBlocklistAdmin(admin.ModelAdmin):
    list_display = ["ip_address", "reason", "is_permanent", "blocked_until"]
    list_filter = ["company", "reason", "is_permanent"]
    search_fields = ["ip_address"]


@admin.register(TwoFactorAuth)
class TwoFactorAuthAdmin(admin.ModelAdmin):
    list_display = ["user", "is_enabled", "method"]
    list_filter = ["company", "is_enabled", "method"]
    search_fields = ["user__username"]


@admin.register(UsuárioSession)
class UsuárioSessionAdmin(admin.ModelAdmin):
    list_display = ["user", "ip_address", "device_type", "login_time", "is_active"]
    list_filter = ["company", "device_type", "is_active", "login_time"]
    search_fields = ["user__username", "ip_address"]
    readonly_fields = ["login_time", "last_activity"]


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "user", "ip_address", "severity", "created_at"]
    list_filter = ["company", "event_type", "severity", "created_at"]
    search_fields = ["user__username", "ip_address"]
    date_hierarchy = "created_at"


@admin.register(AuditoriaConfig)
class AuditoriaConfigAdmin(admin.ModelAdmin):
    list_display = ["company", "require_2fa", "max_failed_login_attempts"]
    list_filter = ["company"]
