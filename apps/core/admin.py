"""Core app admin configuration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company, CompanyDomain, User, UserPermission, AuditLog


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "email", "subscription_status", "created_at")
    search_fields = ("name", "email", "slug")
    list_filter = ("subscription_status", "is_verified", "created_at")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(CompanyDomain)
class CompanyDomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "company", "is_primary", "created_at")
    search_fields = ("domain", "company__name")
    list_filter = ("is_primary", "created_at")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin."""
    list_display = ("username", "email", "company", "is_staff", "is_active")
    list_filter = ("company", "is_staff", "is_active", "groups")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Tenant Info", {"fields": ("company",)}),
        ("Profile", {"fields": ("phone", "avatar", "bio", "language", "timezone")}),
        ("Role", {"fields": ("department", "job_title", "is_employee", "is_contractor")}),
        ("Security", {"fields": ("is_verified", "email_verified", "two_factor_enabled")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Tenant Info", {"fields": ("company",)}),
    )


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ("user", "module", "permission_level", "company")
    list_filter = ("company", "module", "permission_level")
    search_fields = ("user__username", "user__email")


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "module", "object_type", "created_at", "company")
    list_filter = ("company", "action", "module", "created_at")
    search_fields = ("user__username", "object_type", "object_id", "ip_address")
    readonly_fields = ("created_at", "changes", "ip_address", "user_agent")
