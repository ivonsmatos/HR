"""
============================================================================
Zero-Trust Security - Django Admin Configuration
============================================================================

Configuração do Django Admin para gerenciamento das entidades de segurança
Zero-Trust. Interface administrativa para monitoramento e gestão de 
dispositivos, políticas, contextos de acesso e ameaças.

@version 1.0.0
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import (
    TrustedDevice,
    AccessContext,
    ContinuousAuth,
    SecurityPolicy,
    UserBehaviorProfile,
    APISecurityToken,
    ThreatIndicator,
)


# ============================================================================
# TRUSTED DEVICE ADMIN
# ============================================================================

@admin.register(TrustedDevice)
class TrustedDeviceAdmin(admin.ModelAdmin):
    """
    Administração de dispositivos confiáveis.
    """
    list_display = [
        'device_name',
        'user_link',
        'trust_level_badge',
        'device_type',
        'is_active',
        'last_seen_formatted',
    ]
    list_filter = ['trust_level', 'device_type', 'is_active', 'verified']
    search_fields = ['device_name', 'user__username', 'user__email', 'device_fingerprint']
    readonly_fields = ['device_fingerprint', 'first_seen', 'last_seen', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Identificação', {
            'fields': ('user', 'device_name', 'device_type', 'device_fingerprint')
        }),
        ('Confiança', {
            'fields': ('trust_level', 'is_active', 'verified', 'verified_at')
        }),
        ('Metadados', {
            'fields': ('user_agent', 'platform', 'browser', 'browser_version')
        }),
        ('Localização', {
            'fields': ('ip_address', 'country', 'city')
        }),
        ('Timestamps', {
            'fields': ('first_seen', 'last_seen', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:core_usuario_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Usuário'
    
    def trust_level_badge(self, obj):
        colors = {
            'untrusted': '#dc2626',
            'basic': '#f59e0b',
            'elevated': '#3b82f6',
            'corporate': '#10b981',
        }
        color = colors.get(obj.trust_level, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_trust_level_display()
        )
    trust_level_badge.short_description = 'Nível de Confiança'
    
    def last_seen_formatted(self, obj):
        if not obj.last_seen:
            return '-'
        delta = timezone.now() - obj.last_seen
        if delta.days > 30:
            return format_html('<span style="color: #dc2626;">{}</span>', obj.last_seen.strftime('%d/%m/%Y'))
        return obj.last_seen.strftime('%d/%m/%Y %H:%M')
    last_seen_formatted.short_description = 'Último Acesso'
    
    actions = ['revoke_trust', 'elevate_trust', 'mark_verified']
    
    @admin.action(description='Revogar confiança dos dispositivos selecionados')
    def revoke_trust(self, request, queryset):
        queryset.update(trust_level='untrusted', is_active=False)
    
    @admin.action(description='Elevar confiança para Corporate')
    def elevate_trust(self, request, queryset):
        queryset.update(trust_level='corporate', verified=True, verified_at=timezone.now())
    
    @admin.action(description='Marcar como verificado')
    def mark_verified(self, request, queryset):
        queryset.update(verified=True, verified_at=timezone.now())


# ============================================================================
# ACCESS CONTEXT ADMIN
# ============================================================================

@admin.register(AccessContext)
class AccessContextAdmin(admin.ModelAdmin):
    """
    Administração de contextos de acesso.
    """
    list_display = [
        'id_short',
        'user_link',
        'resource_path_truncated',
        'risk_score_badge',
        'decision_badge',
        'created_at',
    ]
    list_filter = ['decision', 'risk_level', 'created_at']
    search_fields = ['user__username', 'resource_path', 'ip_address']
    readonly_fields = ['request_id', 'created_at', 'evaluated_at']
    date_hierarchy = 'created_at'
    
    def id_short(self, obj):
        return obj.request_id[:8] + '...'
    id_short.short_description = 'Request ID'
    
    def user_link(self, obj):
        if not obj.user:
            return 'Anônimo'
        url = reverse('admin:core_usuario_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Usuário'
    
    def resource_path_truncated(self, obj):
        path = obj.resource_path
        return path[:50] + '...' if len(path) > 50 else path
    resource_path_truncated.short_description = 'Recurso'
    
    def risk_score_badge(self, obj):
        score = obj.risk_score
        if score >= 70:
            color = '#10b981'
        elif score >= 50:
            color = '#f59e0b'
        elif score >= 30:
            color = '#f97316'
        else:
            color = '#dc2626'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, f'{score}%'
        )
    risk_score_badge.short_description = 'Risk Score'
    
    def decision_badge(self, obj):
        colors = {
            'allow': '#10b981',
            'deny': '#dc2626',
            'challenge': '#f59e0b',
            'monitor': '#3b82f6',
        }
        color = colors.get(obj.decision, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_decision_display()
        )
    decision_badge.short_description = 'Decisão'


# ============================================================================
# CONTINUOUS AUTH ADMIN
# ============================================================================

@admin.register(ContinuousAuth)
class ContinuousAuthAdmin(admin.ModelAdmin):
    """
    Administração de autenticação contínua.
    """
    list_display = [
        'session_id_short',
        'user_link',
        'confidence_score_badge',
        'auth_factors_count',
        'is_valid_badge',
        'expires_at',
    ]
    list_filter = ['is_valid', 'created_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['session_id', 'created_at']
    
    def session_id_short(self, obj):
        return obj.session_id[:12] + '...'
    session_id_short.short_description = 'Sessão'
    
    def user_link(self, obj):
        url = reverse('admin:core_usuario_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Usuário'
    
    def confidence_score_badge(self, obj):
        score = obj.confidence_score
        if score >= 80:
            color = '#10b981'
        elif score >= 60:
            color = '#3b82f6'
        elif score >= 40:
            color = '#f59e0b'
        else:
            color = '#dc2626'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, f'{score}%'
        )
    confidence_score_badge.short_description = 'Confiança'
    
    def auth_factors_count(self, obj):
        factors = obj.auth_factors or []
        return len(factors)
    auth_factors_count.short_description = 'Fatores'
    
    def is_valid_badge(self, obj):
        if obj.is_valid:
            return format_html('<span style="color: #10b981;">✓ Válido</span>')
        return format_html('<span style="color: #dc2626;">✕ Inválido</span>')
    is_valid_badge.short_description = 'Status'


# ============================================================================
# SECURITY POLICY ADMIN
# ============================================================================

@admin.register(SecurityPolicy)
class SecurityPolicyAdmin(admin.ModelAdmin):
    """
    Administração de políticas de segurança.
    """
    list_display = [
        'name',
        'is_active_badge',
        'priority',
        'resource_pattern',
        'required_trust_level',
        'updated_at',
    ]
    list_filter = ['is_active', 'required_trust_level', 'require_mfa', 'deny_vpn']
    search_fields = ['name', 'description', 'resource_pattern']
    ordering = ['-priority']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('name', 'description', 'is_active', 'priority')
        }),
        ('Escopo', {
            'fields': ('resource_pattern', 'allowed_methods')
        }),
        ('Requisitos de Segurança', {
            'fields': ('required_trust_level', 'min_risk_score', 'require_mfa', 'deny_vpn', 'max_session_age')
        }),
        ('Geolocalização', {
            'fields': ('allowed_countries', 'denied_countries')
        }),
        ('Horário', {
            'fields': ('allowed_hours_start', 'allowed_hours_end', 'allowed_days')
        }),
    )
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981;">● Ativa</span>')
        return format_html('<span style="color: #dc2626;">○ Inativa</span>')
    is_active_badge.short_description = 'Status'


# ============================================================================
# USER BEHAVIOR PROFILE ADMIN
# ============================================================================

@admin.register(UserBehaviorProfile)
class UserBehaviorProfileAdmin(admin.ModelAdmin):
    """
    Administração de perfis comportamentais.
    """
    list_display = [
        'user_link',
        'risk_score_badge',
        'avg_requests_per_day',
        'typical_hours_display',
        'anomalies_detected',
        'updated_at',
    ]
    list_filter = ['updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_link(self, obj):
        url = reverse('admin:core_usuario_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Usuário'
    
    def risk_score_badge(self, obj):
        score = obj.risk_score
        if score <= 20:
            color = '#10b981'
        elif score <= 40:
            color = '#3b82f6'
        elif score <= 60:
            color = '#f59e0b'
        else:
            color = '#dc2626'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, f'{score}%'
        )
    risk_score_badge.short_description = 'Risco'
    
    def typical_hours_display(self, obj):
        hours = obj.typical_hours or {}
        if not hours:
            return '-'
        start = hours.get('start', '?')
        end = hours.get('end', '?')
        return f'{start}h - {end}h'
    typical_hours_display.short_description = 'Horário Típico'


# ============================================================================
# API SECURITY TOKEN ADMIN
# ============================================================================

@admin.register(APISecurityToken)
class APISecurityTokenAdmin(admin.ModelAdmin):
    """
    Administração de tokens de API.
    """
    list_display = [
        'name',
        'user_link',
        'scopes_display',
        'is_active_badge',
        'rate_limit',
        'expires_at',
        'last_used_at',
    ]
    list_filter = ['is_active', 'expires_at', 'created_at']
    search_fields = ['name', 'user__username', 'token_prefix']
    readonly_fields = ['token_hash', 'token_prefix', 'created_at', 'last_used_at']
    
    def user_link(self, obj):
        url = reverse('admin:core_usuario_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)
    user_link.short_description = 'Usuário'
    
    def scopes_display(self, obj):
        scopes = obj.scopes or []
        if len(scopes) <= 3:
            return ', '.join(scopes)
        return f'{", ".join(scopes[:3])} +{len(scopes)-3}'
    scopes_display.short_description = 'Escopos'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981;">● Ativo</span>')
        return format_html('<span style="color: #dc2626;">○ Inativo</span>')
    is_active_badge.short_description = 'Status'
    
    actions = ['revoke_tokens', 'extend_expiration']
    
    @admin.action(description='Revogar tokens selecionados')
    def revoke_tokens(self, request, queryset):
        queryset.update(is_active=False)
    
    @admin.action(description='Estender expiração em 30 dias')
    def extend_expiration(self, request, queryset):
        from datetime import timedelta
        for token in queryset:
            if token.expires_at:
                token.expires_at = token.expires_at + timedelta(days=30)
                token.save()


# ============================================================================
# THREAT INDICATOR ADMIN
# ============================================================================

@admin.register(ThreatIndicator)
class ThreatIndicatorAdmin(admin.ModelAdmin):
    """
    Administração de indicadores de ameaça.
    """
    list_display = [
        'indicator_value_truncated',
        'indicator_type_badge',
        'severity_badge',
        'source',
        'is_active_badge',
        'valid_until',
    ]
    list_filter = ['indicator_type', 'severity', 'is_active', 'source']
    search_fields = ['indicator_value', 'description', 'source']
    date_hierarchy = 'created_at'
    
    def indicator_value_truncated(self, obj):
        val = obj.indicator_value
        return val[:30] + '...' if len(val) > 30 else val
    indicator_value_truncated.short_description = 'Indicador'
    
    def indicator_type_badge(self, obj):
        colors = {
            'ip': '#3b82f6',
            'domain': '#8b5cf6',
            'hash': '#ec4899',
            'email': '#06b6d4',
            'pattern': '#f59e0b',
        }
        color = colors.get(obj.indicator_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_indicator_type_display()
        )
    indicator_type_badge.short_description = 'Tipo'
    
    def severity_badge(self, obj):
        colors = {
            'low': '#10b981',
            'medium': '#f59e0b',
            'high': '#f97316',
            'critical': '#dc2626',
        }
        color = colors.get(obj.severity, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_badge.short_description = 'Severidade'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html('<span style="color: #10b981;">● Ativo</span>')
        return format_html('<span style="color: #dc2626;">○ Inativo</span>')
    is_active_badge.short_description = 'Status'
    
    actions = ['activate_indicators', 'deactivate_indicators']
    
    @admin.action(description='Ativar indicadores selecionados')
    def activate_indicators(self, request, queryset):
        queryset.update(is_active=True)
    
    @admin.action(description='Desativar indicadores selecionados')
    def deactivate_indicators(self, request, queryset):
        queryset.update(is_active=False)
