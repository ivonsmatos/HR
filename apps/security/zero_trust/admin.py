"""
============================================================================
Zero-Trust Security - Django Admin Configuration
============================================================================

Configuração simplificada do Django Admin para gerenciamento das entidades 
de segurança Zero-Trust.

@version 1.0.2
"""

from django.contrib import admin

from .models import (
    TrustedDevice,
    AccessContext,
    ContinuousAuth,
    SecurityPolicy,
    UserBehaviorProfile,
    APISecurityToken,
    ThreatIndicator,
)


@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ['device_name', 'user', 'trust_level', 'device_type', 'is_active', 'last_seen']
    list_filter = ['trust_level', 'device_type', 'is_active', 'is_verified']
    search_fields = ['device_name', 'user__username', 'device_fingerprint']
    readonly_fields = ['device_fingerprint', 'device_id', 'created_at', 'updated_at']


@admin.register(AccessContext)
class AccessContextAdmin(admin.ModelAdmin):
    list_display = ['request_id', 'user', 'resource_path', 'risk_score', 'decision', 'access_time']
    list_filter = ['decision', 'risk_level', 'access_time']
    search_fields = ['user__username', 'resource_path', 'ip_address']
    readonly_fields = ['request_id', 'created_at']


@admin.register(ContinuousAuth)
class ContinuousAuthAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'user', 'confidence_score', 'is_active', 'session_expires']
    list_filter = ['is_active', 'auth_level', 'created_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['session_key', 'created_at']


@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'priority', 'policy_type', 'updated_at']
    list_filter = ['is_active', 'policy_type']
    search_fields = ['name', 'description']
    ordering = ['-priority']


@admin.register(UserBehaviorProfile)
class UserBehaviorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'baseline_risk_score', 'anomaly_count_30d', 'profile_maturity', 'last_profile_update']
    list_filter = ['profile_maturity']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at', 'last_profile_update']


@admin.register(APISecurityToken)
class APISecurityTokenAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'token_type', 'is_active', 'expires_at', 'created_at']
    list_filter = ['is_active', 'token_type', 'created_at']
    search_fields = ['name', 'user__username']
    readonly_fields = ['token_hash', 'token_prefix', 'created_at']


@admin.register(ThreatIndicator)
class ThreatIndicatorAdmin(admin.ModelAdmin):
    list_display = ['indicator_value', 'indicator_type', 'threat_level', 'is_active', 'expires_at']
    list_filter = ['indicator_type', 'threat_level', 'is_active']
    search_fields = ['indicator_value', 'description', 'source']
