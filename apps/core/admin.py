"""Core app admin configuration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Empresa, EmpresaDomain, Usuário, UsuárioPermission, AuditoriaLog


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "email", "subscription_status", "is_active", "created_at"]
    list_filter = ["subscription_status", "is_active", "industry"]
    search_fields = ["name", "email", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Informaçãormações Básicas", {"fields": ("name", "slug", "description")}),
        ("Contato", {"fields": ("email", "phone", "website")}),
        ("Endereço", {"fields": ("address", "city", "state", "postal_code", "country")}),
        ("Organização", {"fields": ("industry", "company_size", "currency", "timezone")}),
        ("Marca", {"fields": ("logo",)}),
        ("Assinatura", {"fields": ("subscription_plan", "subscription_status", "trial_ends_at", "subscription_ends_at")}),
        ("Status", {"fields": ("is_verified", "is_on_trial", "is_active")}),
    )


@admin.register(EmpresaDomain)
class EmpresaDomainAdmin(admin.ModelAdmin):
    list_display = ["domain", "company", "is_primary", "created_at"]
    list_filter = ["is_primary", "created_at", "company"]
    search_fields = ["domain", "company__name"]
    fieldsets = (
        ("Informaçãormações do Domínio", {"fields": ("domain", "company", "is_primary")}),
        ("Metadados", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Usuário)
class UsuárioAdmin(BaseUserAdmin):
    list_display = ["username", "email", "company", "is_employee", "is_active"]
    list_filter = ["company", "is_active", "is_employee", "is_contractor"]
    search_fields = ["username", "email", "first_name", "last_name"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Empresa & Perfil", {"fields": ("company", "avatar", "phone", "bio")}),
        ("Detalhes de RH", {"fields": ("department", "job_title", "is_employee", "is_contractor")}),
        ("Segurança", {"fields": ("two_factor_enabled", "email_verified", "email_verified_at")}),
        ("Preferências", {"fields": ("language", "timezone")}),
        ("Atividade", {"fields": ("last_login_ip", "last_activity", "login_count")}),
    )


@admin.register(UsuárioPermission)
class UsuárioPermissionAdmin(admin.ModelAdmin):
    list_display = ["user", "module", "permission_level", "company", "is_active"]
    list_filter = ["company", "module", "permission_level", "is_active"]
    search_fields = ["user__username", "module"]


@admin.register(AuditoriaLog)
class AuditoriaLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "module", "created_at", "ip_address"]
    list_filter = ["company", "action", "created_at"]
    search_fields = ["user__username", "module", "object_id"]
    date_hierarchy = "created_at"
    readonly_fields = ["user", "action", "module", "object_type", "object_id", "created_at"]
