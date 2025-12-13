"""
============================================================================
Zero-Trust Security - Serializers
============================================================================

Serializers para a API REST do módulo Zero-Trust Security.
Implementa serialização/deserialização dos modelos de segurança.

@version 1.0.0
"""

from rest_framework import serializers
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
# TRUSTED DEVICE SERIALIZERS
# ============================================================================

class TrustedDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer para dispositivos confiáveis (leitura).
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    trust_level_display = serializers.CharField(source='get_trust_level_display', read_only=True)
    device_type_display = serializers.CharField(source='get_device_type_display', read_only=True)
    days_since_last_seen = serializers.SerializerMethodField()
    
    class Meta:
        model = TrustedDevice
        fields = [
            'id', 'device_name', 'device_type', 'device_type_display',
            'trust_level', 'trust_level_display', 'is_active', 'verified',
            'verified_at', 'first_seen', 'last_seen', 'days_since_last_seen',
            'ip_address', 'country', 'city', 'platform', 'browser',
            'user_email', 'created_at', 'updated_at',
        ]
        read_only_fields = ['device_fingerprint', 'first_seen', 'last_seen', 'created_at', 'updated_at']
    
    def get_days_since_last_seen(self, obj):
        if not obj.last_seen:
            return None
        delta = timezone.now() - obj.last_seen
        return delta.days


class TrustedDeviceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de dispositivos.
    """
    class Meta:
        model = TrustedDevice
        fields = ['device_name']
    
    def create(self, validated_data):
        from .services import DeviceTrustService
        request = self.context.get('request')
        return DeviceTrustService.register_device(
            request, 
            validated_data.get('device_name', 'Dispositivo sem nome')
        )


# ============================================================================
# ACCESS CONTEXT SERIALIZERS
# ============================================================================

class AccessContextSerializer(serializers.ModelSerializer):
    """
    Serializer para contextos de acesso.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    decision_display = serializers.CharField(source='get_decision_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)
    
    class Meta:
        model = AccessContext
        fields = [
            'id', 'request_id', 'user_username', 'resource_path', 'method',
            'ip_address', 'risk_score', 'risk_level', 'risk_level_display',
            'decision', 'decision_display', 'factors', 'created_at', 'evaluated_at',
        ]
        read_only_fields = ['request_id', 'created_at', 'evaluated_at']


# ============================================================================
# CONTINUOUS AUTH SERIALIZERS
# ============================================================================

class ContinuousAuthSerializer(serializers.ModelSerializer):
    """
    Serializer para autenticação contínua.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    time_remaining = serializers.SerializerMethodField()
    auth_factors_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ContinuousAuth
        fields = [
            'id', 'session_id', 'user_username', 'confidence_score',
            'auth_factors', 'auth_factors_count', 'is_valid', 'expires_at',
            'time_remaining', 'last_verification', 'created_at',
        ]
        read_only_fields = ['session_id', 'created_at']
    
    def get_time_remaining(self, obj):
        if not obj.expires_at or not obj.is_valid:
            return 0
        delta = obj.expires_at - timezone.now()
        return max(0, int(delta.total_seconds()))
    
    def get_auth_factors_count(self, obj):
        return len(obj.auth_factors or [])


# ============================================================================
# SECURITY POLICY SERIALIZERS
# ============================================================================

class SecurityPolicySerializer(serializers.ModelSerializer):
    """
    Serializer para políticas de segurança.
    """
    required_trust_level_display = serializers.CharField(
        source='get_required_trust_level_display', read_only=True
    )
    
    class Meta:
        model = SecurityPolicy
        fields = [
            'id', 'name', 'description', 'is_active', 'priority',
            'resource_pattern', 'allowed_methods', 'required_trust_level',
            'required_trust_level_display', 'min_risk_score', 'require_mfa',
            'deny_vpn', 'max_session_age', 'allowed_countries', 'denied_countries',
            'allowed_hours_start', 'allowed_hours_end', 'allowed_days',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_priority(self, value):
        if value < 0 or value > 1000:
            raise serializers.ValidationError('Prioridade deve estar entre 0 e 1000.')
        return value
    
    def validate_min_risk_score(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError('Score deve estar entre 0 e 100.')
        return value


# ============================================================================
# USER BEHAVIOR PROFILE SERIALIZERS
# ============================================================================

class UserBehaviorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para perfis comportamentais.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    risk_category = serializers.SerializerMethodField()
    
    class Meta:
        model = UserBehaviorProfile
        fields = [
            'id', 'user_username', 'user_email', 'risk_score', 'risk_category',
            'typical_hours', 'typical_locations', 'typical_devices',
            'avg_requests_per_day', 'anomalies_detected', 'last_anomaly',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_risk_category(self, obj):
        score = obj.risk_score
        if score <= 20:
            return 'baixo'
        elif score <= 40:
            return 'moderado'
        elif score <= 60:
            return 'elevado'
        else:
            return 'crítico'


# ============================================================================
# API SECURITY TOKEN SERIALIZERS
# ============================================================================

class APISecurityTokenSerializer(serializers.ModelSerializer):
    """
    Serializer para tokens de API (leitura).
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    is_expired = serializers.SerializerMethodField()
    scopes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = APISecurityToken
        fields = [
            'id', 'name', 'token_prefix', 'user_username', 'scopes',
            'scopes_count', 'allowed_ips', 'rate_limit', 'is_active',
            'expires_at', 'is_expired', 'last_used_at', 'usage_count',
            'created_at',
        ]
        read_only_fields = ['token_prefix', 'created_at', 'last_used_at', 'usage_count']
    
    def get_is_expired(self, obj):
        if not obj.expires_at:
            return False
        return obj.expires_at < timezone.now()
    
    def get_scopes_count(self, obj):
        return len(obj.scopes or [])


class APISecurityTokenCreateSerializer(serializers.Serializer):
    """
    Serializer para criação de tokens de API.
    """
    name = serializers.CharField(max_length=255)
    scopes = serializers.ListField(
        child=serializers.CharField(),
        default=['read']
    )
    expires_days = serializers.IntegerField(min_value=1, max_value=365, default=30)
    allowed_ips = serializers.ListField(
        child=serializers.IPAddressField(),
        required=False,
        default=list
    )
    rate_limit = serializers.IntegerField(min_value=10, max_value=10000, default=1000)
    
    def validate_scopes(self, value):
        valid_scopes = ['read', 'write', 'delete', 'admin', 'lgpd', 'nist', 'security']
        for scope in value:
            if scope not in valid_scopes:
                raise serializers.ValidationError(f'Escopo inválido: {scope}')
        return value


# ============================================================================
# THREAT INDICATOR SERIALIZERS
# ============================================================================

class ThreatIndicatorSerializer(serializers.ModelSerializer):
    """
    Serializer para indicadores de ameaça.
    """
    indicator_type_display = serializers.CharField(
        source='get_indicator_type_display', read_only=True
    )
    severity_display = serializers.CharField(
        source='get_severity_display', read_only=True
    )
    is_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = ThreatIndicator
        fields = [
            'id', 'indicator_type', 'indicator_type_display', 'indicator_value',
            'severity', 'severity_display', 'source', 'description',
            'is_active', 'valid_until', 'is_valid', 'times_matched',
            'last_matched', 'created_at',
        ]
        read_only_fields = ['times_matched', 'last_matched', 'created_at']
    
    def get_is_valid(self, obj):
        if not obj.valid_until:
            return obj.is_active
        return obj.is_active and obj.valid_until > timezone.now()


# ============================================================================
# RISK ASSESSMENT SERIALIZERS
# ============================================================================

class RiskAssessmentSerializer(serializers.Serializer):
    """
    Serializer para resultados de avaliação de risco.
    """
    risk_score = serializers.IntegerField(min_value=0, max_value=100)
    risk_level = serializers.ChoiceField(choices=['low', 'medium', 'high', 'critical'])
    decision = serializers.ChoiceField(choices=['allow', 'deny', 'challenge', 'monitor'])
    factors = serializers.DictField(required=False)
    recommendations = serializers.ListField(
        child=serializers.DictField(),
        required=False
    )
