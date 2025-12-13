"""
SyncRH - Zero-Trust Security Models
====================================
Modelos para implementação de segurança Zero-Trust

Referências:
- NIST SP 800-207 (Zero Trust Architecture)
- Microsoft Zero Trust Maturity Model
- Google BeyondCorp
"""

import uuid
import hashlib
import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class BaseZeroTrustModel(models.Model):
    """Base model para todos os modelos Zero-Trust."""
    
    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


# =============================================================================
# 1. DEVICE TRUST & REGISTRATION
# =============================================================================

class TrustedDevice(BaseZeroTrustModel):
    """
    Dispositivos confiáveis registrados.
    Zero-Trust requer verificação de dispositivo + usuário.
    """
    
    DEVICE_TYPES = [
        ('desktop', 'Desktop/Laptop'),
        ('mobile', 'Smartphone'),
        ('tablet', 'Tablet'),
        ('terminal', 'Terminal/Kiosk'),
        ('api_client', 'API Client'),
    ]
    
    TRUST_LEVELS = [
        ('untrusted', 'Não Confiável'),
        ('limited', 'Confiança Limitada'),
        ('standard', 'Confiança Padrão'),
        ('elevated', 'Confiança Elevada'),
        ('corporate', 'Dispositivo Corporativo'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trusted_devices'
    )
    
    # Identificação do dispositivo
    device_id = models.CharField(max_length=255, unique=True, db_index=True)
    device_fingerprint = models.CharField(max_length=512, db_index=True)
    device_name = models.CharField(max_length=100, blank=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='desktop')
    
    # Informações técnicas
    user_agent = models.TextField(blank=True)
    browser_name = models.CharField(max_length=50, blank=True)
    browser_version = models.CharField(max_length=20, blank=True)
    os_name = models.CharField(max_length=50, blank=True)
    os_version = models.CharField(max_length=20, blank=True)
    screen_resolution = models.CharField(max_length=20, blank=True)
    
    # Nível de confiança
    trust_level = models.CharField(max_length=20, choices=TRUST_LEVELS, default='untrusted')
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='verified_devices'
    )
    
    # Controle de acesso
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    blocked_reason = models.TextField(blank=True)
    
    # Última atividade
    last_seen = models.DateTimeField(null=True, blank=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)
    last_location = models.CharField(max_length=100, blank=True)
    
    # PWA específico
    is_pwa_installed = models.BooleanField(default=False)
    push_subscription = models.JSONField(null=True, blank=True)
    
    class Meta:
        app_label = 'zero_trust'
        verbose_name = 'Dispositivo Confiável'
        verbose_name_plural = 'Dispositivos Confiáveis'
        ordering = ['-last_seen']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['device_fingerprint']),
            models.Index(fields=['trust_level', 'is_verified']),
        ]
    
    def __str__(self):
        return f"{self.device_name or self.device_type} - {self.user.username}"
    
    def generate_device_id(self, request):
        """Gera ID único baseado em características do dispositivo."""
        components = [
            request.META.get('HTTP_USER_AGENT', ''),
            request.META.get('HTTP_ACCEPT_LANGUAGE', ''),
            request.META.get('HTTP_ACCEPT_ENCODING', ''),
        ]
        raw = '|'.join(components)
        return hashlib.sha256(raw.encode()).hexdigest()


# =============================================================================
# 2. ACCESS CONTEXT & SIGNALS
# =============================================================================

class AccessContext(BaseZeroTrustModel):
    """
    Contexto de cada tentativa de acesso.
    Zero-Trust avalia contexto em CADA requisição.
    """
    
    RISK_LEVELS = [
        ('low', 'Baixo'),
        ('medium', 'Médio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]
    
    DECISIONS = [
        ('allow', 'Permitido'),
        ('deny', 'Negado'),
        ('challenge', 'Desafio MFA'),
        ('step_up', 'Step-Up Auth'),
        ('block', 'Bloqueado'),
    ]
    
    # Identificação
    session_id = models.CharField(max_length=255, db_index=True)
    request_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    
    # Usuário e dispositivo
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='access_contexts'
    )
    device = models.ForeignKey(
        TrustedDevice,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='access_contexts'
    )
    
    # Contexto de rede
    ip_address = models.GenericIPAddressField(db_index=True)
    ip_type = models.CharField(max_length=20, blank=True)  # corporate, vpn, public, tor
    geo_country = models.CharField(max_length=2, blank=True)
    geo_city = models.CharField(max_length=100, blank=True)
    geo_coordinates = models.CharField(max_length=50, blank=True)
    asn = models.CharField(max_length=50, blank=True)
    isp = models.CharField(max_length=100, blank=True)
    
    # Contexto temporal
    access_time = models.DateTimeField(auto_now_add=True)
    is_business_hours = models.BooleanField(default=True)
    is_unusual_time = models.BooleanField(default=False)
    
    # Recurso acessado
    resource_type = models.CharField(max_length=50)  # api, view, file, admin
    resource_path = models.CharField(max_length=500)
    resource_method = models.CharField(max_length=10)  # GET, POST, etc
    resource_sensitivity = models.CharField(max_length=20, default='normal')
    
    # Avaliação de risco
    risk_score = models.IntegerField(default=0)  # 0-100
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='low')
    risk_factors = models.JSONField(default=list)
    
    # Decisão
    decision = models.CharField(max_length=20, choices=DECISIONS)
    decision_reason = models.TextField(blank=True)
    policy_applied = models.CharField(max_length=100, blank=True)
    
    # Resultado
    was_successful = models.BooleanField(default=True)
    response_code = models.IntegerField(null=True, blank=True)
    
    class Meta:
        app_label = 'zero_trust'
        verbose_name = 'Contexto de Acesso'
        verbose_name_plural = 'Contextos de Acesso'
        ordering = ['-access_time']
        indexes = [
            models.Index(fields=['user', '-access_time']),
            models.Index(fields=['ip_address', '-access_time']),
            models.Index(fields=['risk_level', '-access_time']),
            models.Index(fields=['decision', '-access_time']),
        ]
    
    def __str__(self):
        return f"{self.request_id} - {self.decision}"


# =============================================================================
# 3. CONTINUOUS AUTHENTICATION
# =============================================================================

class ContinuousAuth(BaseZeroTrustModel):
    """
    Autenticação contínua - verifica identidade periodicamente.
    Implementa conceito de "session confidence score".
    """
    
    AUTH_METHODS = [
        ('password', 'Senha'),
        ('mfa_totp', 'MFA - TOTP'),
        ('mfa_sms', 'MFA - SMS'),
        ('mfa_email', 'MFA - Email'),
        ('biometric', 'Biometria'),
        ('passkey', 'Passkey/WebAuthn'),
        ('behavioral', 'Análise Comportamental'),
        ('device_trust', 'Confiança do Dispositivo'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='continuous_auths'
    )
    device = models.ForeignKey(
        TrustedDevice,
        on_delete=models.CASCADE,
        related_name='continuous_auths'
    )
    
    # Sessão
    session_key = models.CharField(max_length=255, unique=True)
    session_started = models.DateTimeField(auto_now_add=True)
    session_expires = models.DateTimeField()
    
    # Score de confiança (0-100)
    confidence_score = models.IntegerField(default=100)
    min_confidence_threshold = models.IntegerField(default=70)
    
    # Última verificação
    last_verification = models.DateTimeField(auto_now_add=True)
    verification_method = models.CharField(max_length=20, choices=AUTH_METHODS)
    next_verification_due = models.DateTimeField()
    
    # Fatores de autenticação usados
    auth_factors_used = models.JSONField(
        default=list,
        blank=True
    )
    auth_level = models.IntegerField(default=1)  # 1=single, 2=MFA, 3=strong
    
    # Estado
    is_active = models.BooleanField(default=True)
    requires_reauthentication = models.BooleanField(default=False)
    reauthentication_reason = models.CharField(max_length=100, blank=True)
    
    class Meta:
        app_label = 'zero_trust'
        verbose_name = 'Autenticação Contínua'
        verbose_name_plural = 'Autenticações Contínuas'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        return f"Auth {self.user.username} - Score: {self.confidence_score}"
    
    def decay_confidence(self, amount=5):
        """Reduz score de confiança ao longo do tempo."""
        self.confidence_score = max(0, self.confidence_score - amount)
        if self.confidence_score < self.min_confidence_threshold:
            self.requires_reauthentication = True
            self.reauthentication_reason = 'Confidence score below threshold'
        self.save(update_fields=['confidence_score', 'requires_reauthentication', 
                                  'reauthentication_reason', 'updated_at'])
    
    def boost_confidence(self, method, amount=20):
        """Aumenta score após verificação bem-sucedida."""
        self.confidence_score = min(100, self.confidence_score + amount)
        self.last_verification = timezone.now()
        self.verification_method = method
        self.requires_reauthentication = False
        self.reauthentication_reason = ''
        self.next_verification_due = timezone.now() + timedelta(minutes=30)
        self.save()


# =============================================================================
# 4. MICRO-SEGMENTATION & POLICIES
# =============================================================================

class SecurityPolicy(BaseZeroTrustModel):
    """
    Políticas de segurança granulares.
    Zero-Trust usa micro-segmentação por recurso.
    """
    
    POLICY_TYPES = [
        ('access', 'Controle de Acesso'),
        ('authentication', 'Autenticação'),
        ('data', 'Proteção de Dados'),
        ('network', 'Rede'),
        ('device', 'Dispositivo'),
        ('time', 'Temporal'),
        ('location', 'Geolocalização'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    
    # Escopo
    applies_to_roles = models.JSONField(
        default=list,
        blank=True,
        help_text='Roles afetadas (vazio = todas)'
    )
    applies_to_resources = models.JSONField(
        default=list,
        blank=True,
        help_text='Padrões de URL (regex)'
    )
    
    # Condições (JSON para flexibilidade)
    conditions = models.JSONField(
        default=dict,
        help_text='Condições para ativação da política'
    )
    """
    Exemplo de conditions:
    {
        "require_mfa": true,
        "min_trust_level": "standard",
        "allowed_countries": ["BR"],
        "allowed_hours": {"start": 8, "end": 18},
        "max_risk_score": 50,
        "require_corporate_device": false
    }
    """
    
    # Ações
    action_on_match = models.CharField(
        max_length=20,
        choices=[
            ('allow', 'Permitir'),
            ('deny', 'Negar'),
            ('challenge', 'Solicitar MFA'),
            ('log', 'Apenas Registrar'),
            ('alert', 'Alertar Admin'),
        ],
        default='allow'
    )
    
    # Prioridade e estado
    priority = models.IntegerField(default=100)
    is_active = models.BooleanField(default=True)
    is_enforced = models.BooleanField(default=False)  # False = audit mode
    
    class Meta:
        app_label = 'zero_trust'
        verbose_name = 'Política de Segurança'
        verbose_name_plural = 'Políticas de Segurança'
        ordering = ['priority', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.policy_type})"


# =============================================================================
# 5. BEHAVIORAL ANALYSIS
# =============================================================================

class UserBehaviorProfile(BaseZeroTrustModel):
    """
    Perfil comportamental do usuário.
    Zero-Trust usa análise comportamental para detectar anomalias.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='behavior_profile'
    )
    
    # Padrões de horário
    typical_login_hours = models.JSONField(
        default=dict,
        help_text='Distribuição de horários de login por dia da semana'
    )
    typical_session_duration = models.DurationField(null=True, blank=True)
    
    # Padrões de localização
    typical_locations = models.JSONField(
        default=list,
        blank=True
    )
    typical_ips = models.JSONField(
        default=list,
        blank=True
    )
    
    # Padrões de dispositivo
    known_devices_count = models.IntegerField(default=0)
    primary_device_type = models.CharField(max_length=20, blank=True)
    
    # Padrões de uso
    typical_resources = models.JSONField(
        default=list,
        blank=True
    )
    typical_actions_per_session = models.IntegerField(default=0)
    
    # Métricas de risco
    baseline_risk_score = models.IntegerField(default=20)
    anomaly_count_30d = models.IntegerField(default=0)
    last_anomaly_detected = models.DateTimeField(null=True, blank=True)
    
    # Aprendizado
    profile_maturity = models.CharField(
        max_length=20,
        choices=[
            ('learning', 'Aprendendo'),
            ('baseline', 'Baseline Estabelecido'),
            ('mature', 'Perfil Maduro'),
        ],
        default='learning'
    )
    data_points_collected = models.IntegerField(default=0)
    last_profile_update = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'zero_trust'
        verbose_name = 'Perfil Comportamental'
        verbose_name_plural = 'Perfis Comportamentais'
    
    def __str__(self):
        return f"Behavior Profile - {self.user.username}"
    
    def calculate_anomaly_score(self, context):
        """Calcula score de anomalia baseado no contexto atual."""
        score = 0
        factors = []
        
        # Verificar horário
        current_hour = timezone.now().hour
        if self.typical_login_hours:
            day = timezone.now().strftime('%A').lower()
            typical = self.typical_login_hours.get(day, [])
            if current_hour not in typical:
                score += 15
                factors.append('unusual_time')
        
        # Verificar localização
        if context.get('geo_country') and context['geo_country'] not in self.typical_locations:
            score += 25
            factors.append('new_location')
        
        # Verificar IP
        if context.get('ip_address') and context['ip_address'] not in self.typical_ips:
            score += 10
            factors.append('new_ip')
        
        return score, factors


# =============================================================================
# 6. API SECURITY TOKENS
# =============================================================================

class APISecurityToken(BaseZeroTrustModel):
    """
    Tokens seguros para API com escopo limitado.
    Zero-Trust: tokens com privilégio mínimo e vida curta.
    """
    
    TOKEN_TYPES = [
        ('access', 'Access Token'),
        ('refresh', 'Refresh Token'),
        ('api_key', 'API Key'),
        ('service', 'Service Account'),
        ('webhook', 'Webhook'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='api_tokens',
        null=True, blank=True
    )
    
    # Token info
    name = models.CharField(max_length=100)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    token_hash = models.CharField(max_length=128, unique=True, db_index=True)
    token_prefix = models.CharField(max_length=10)  # Primeiros caracteres para identificação
    
    # Escopo e permissões
    scopes = models.JSONField(
        default=list,
        help_text='Escopos permitidos: read:users, write:employees, etc'
    )
    allowed_ips = models.JSONField(
        default=list,
        blank=True,
        help_text='IPs permitidos (vazio = todos)'
    )
    allowed_resources = models.JSONField(
        default=list,
        blank=True,
        help_text='Padrões de URL permitidos'
    )
    
    # Rate limiting
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_day = models.IntegerField(default=10000)
    
    # Validade
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Uso
    last_used = models.DateTimeField(null=True, blank=True)
    total_requests = models.IntegerField(default=0)
    
    # Revogação
    is_revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoked_reason = models.CharField(max_length=200, blank=True)
    
    class Meta:
        app_label = 'zero_trust'
        verbose_name = 'Token de API'
        verbose_name_plural = 'Tokens de API'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.token_prefix}...)"
    
    @classmethod
    def generate_token(cls):
        """Gera token seguro."""
        token = secrets.token_urlsafe(32)
        return token, hashlib.sha256(token.encode()).hexdigest()
    
    def is_valid(self):
        """Verifica se token é válido."""
        if self.is_revoked or not self.is_active:
            return False
        if self.expires_at < timezone.now():
            return False
        return True


# =============================================================================
# 7. THREAT INTELLIGENCE
# =============================================================================

class ThreatIndicator(BaseZeroTrustModel):
    """
    Indicadores de ameaça para enriquecimento de decisões.
    """
    
    INDICATOR_TYPES = [
        ('ip', 'Endereço IP'),
        ('domain', 'Domínio'),
        ('email', 'Email'),
        ('hash', 'File Hash'),
        ('user_agent', 'User Agent'),
        ('pattern', 'Padrão de Ataque'),
    ]
    
    THREAT_LEVELS = [
        ('info', 'Informativo'),
        ('low', 'Baixo'),
        ('medium', 'Médio'),
        ('high', 'Alto'),
        ('critical', 'Crítico'),
    ]
    
    indicator_type = models.CharField(max_length=20, choices=INDICATOR_TYPES)
    indicator_value = models.CharField(max_length=500, db_index=True)
    threat_level = models.CharField(max_length=20, choices=THREAT_LEVELS)
    
    description = models.TextField(blank=True)
    source = models.CharField(max_length=100)  # Fonte da inteligência
    
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    times_observed = models.IntegerField(default=1)
    
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Tags para categorização
    tags = models.JSONField(
        default=list,
        blank=True
    )
    
    class Meta:
        app_label = 'zero_trust'
        verbose_name = 'Indicador de Ameaça'
        verbose_name_plural = 'Indicadores de Ameaça'
        unique_together = ['indicator_type', 'indicator_value']
        indexes = [
            models.Index(fields=['indicator_type', 'indicator_value']),
            models.Index(fields=['threat_level', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.indicator_type}: {self.indicator_value[:50]}"
