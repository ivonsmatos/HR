"""Core app admin configuration."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Company, CompanyDomain, User, UserPermission, AuditLog


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "email", "subscription_status", "is_active", "created_at"]
    list_filter = ["subscription_status", "is_active", "industry"]
    search_fields = ["name", "email", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Basic Info", {"fields": ("name", "slug", "description")}),
        ("Contact", {"fields": ("email", "phone", "website")}),
        ("Address", {"fields": ("address", "city", "state", "postal_code", "country")}),
        ("Organization", {"fields": ("industry", "company_size", "currency", "timezone")}),
        ("Branding", {"fields": ("logo",)}),
        ("Subscription", {"fields": ("subscription_plan", "subscription_status", "trial_ends_at", "subscription_ends_at")}),
        ("Status", {"fields": ("is_verified", "is_on_trial", "is_active")}),
    )


@admin.register(CompanyDomain)
class CompanyDomainAdmin(admin.ModelAdmin):
    list_display = ["domain", "company", "is_primary", "created_at"]
    list_filter = ["is_primary", "created_at", "company"]
    search_fields = ["domain", "company__name"]
    fieldsets = (
        ("Domain Info", {"fields": ("domain", "company", "is_primary")}),
        ("Metadata", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
    readonly_fields = ["created_at", "updated_at"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "company", "is_employee", "is_active"]
    list_filter = ["company", "is_active", "is_employee", "is_contractor"]
    search_fields = ["username", "email", "first_name", "last_name"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Company & Profile", {"fields": ("company", "avatar", "phone", "bio")}),
        ("HR Details", {"fields": ("department", "job_title", "is_employee", "is_contractor")}),
        ("Security", {"fields": ("two_factor_enabled", "email_verified", "email_verified_at")}),
        ("Preferences", {"fields": ("language", "timezone")}),
        ("Activity", {"fields": ("last_login_ip", "last_activity", "login_count")}),
    )


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ["user", "module", "permission_level", "company", "is_active"]
    list_filter = ["company", "module", "permission_level", "is_active"]
    search_fields = ["user__username", "module"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "module", "created_at", "ip_address"]
    list_filter = ["company", "action", "created_at"]
    search_fields = ["user__username", "module", "object_id"]
    date_hierarchy = "created_at"
    readonly_fields = ["user", "action", "module", "object_type", "object_id", "created_at"]
