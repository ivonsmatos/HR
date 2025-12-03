"""
SECURITY (Security & Auditoria) App Models

Sub-modules:
- AuditoriaLogs: Logging and audit trails
- IpBlocklist: IP blocking for security
- 2FA: Two-factor authentication
- SessionManagement: Active session tracking
- SecurityEvents: Security-related events
"""

from django.db import models
from apps.core.models import TenantAwareModel, Usuário


# ============================================================================
# 1. IP BLOCKLIST SUB-MODULE
# ============================================================================

class IpBlocklist(TenantAwareModel):
    """Blocked IP addresses."""

    ip_address = models.GenericIPAdicionarressField(unique=True)
    reason = models.CharField(
        max_length=50,
        choices=[
            ("brute_force", "Brute Force Attack"),
            ("suspicious_activity", "Suspicious Activity"),
            ("manual_block", "Manual Block"),
            ("phishing", "Phishing Attempt"),
        ],
    )
    blocked_until = models.DateTimeField(null=True, blank=True)
    is_permanent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Lista Bloqueada de IP"
        verbose_name_plural = "Listas Bloqueadas de IP"

    def __str__(self):
        return f"Blocked: {self.ip_address}"


# ============================================================================
# 2. TWO-FACTOR AUTHENTICATION SUB-MODULE
# ============================================================================

class TwoFactorAuth(TenantAwareModel):
    """2FA configuration for users."""

    METHODS = [
        ("email", "Email"),
        ("sms", "SMS"),
        ("authenticator", "Authenticator App"),
    ]

    user = models.OneToOneField(
        Usuário,
        on_delete=models.CASCADE,
        related_name="two_factor_auth",
    )
    is_enabled = models.BooleanField(default=False)
    method = models.CharField(max_length=50, choices=METHODS, default="email")
    backup_codes = models.JSONField(default=list, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Autenticação de Dois Fatores"
        verbose_name_plural = "Autenticações de Dois Fatores"

    def __str__(self):
        return f"2FA - {self.user.username}"


# ============================================================================
# 3. SESSION MANAGEMENT SUB-MODULE
# ============================================================================

class UsuárioSession(TenantAwareModel):
    """Active user sessions."""

    user = models.ForeignKey(
        Usuário,
        on_delete=models.CASCADE,
        related_name="sessions",
    )
    token = models.CharField(max_length=500)
    ip_address = models.GenericIPAdicionarressField()
    user_agent = models.TextField()
    device_type = models.CharField(
        max_length=20,
        choices=[
            ("desktop", "Desktop"),
            ("mobile", "Mobile"),
            ("tablet", "Tablet"),
            ("other", "Other"),
        ],
        default="desktop",
    )
    login_time = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Sessão do Usuário"
        verbose_name_plural = "Sessões do Usuário"

    def __str__(self):
        return f"{self.user.username} - {self.ip_address}"


# ============================================================================
# 4. SECURITY EVENTS SUB-MODULE
# ============================================================================

class SecurityEvent(TenantAwareModel):
    """Security-related events."""

    EVENT_TYPES = [
        ("login_success", "Sucessoful Entrar"),
        ("login_failed", "Failed Entrar"),
        ("password_changed", "Senha Alterard"),
        ("permission_granted", "Permission Granted"),
        ("permission_revoked", "Permission Revoked"),
        ("data_export", "Data Exportar"),
        ("data_import", "Data Importar"),
        ("brute_force_attempt", "Brute Force Attempt"),
        ("suspicious_activity", "Suspicious Activity"),
        ("phishing_attempt", "Phishing Attempt"),
        ("unauthorized_access", "Unauthorized Access Attempt"),
    ]

    user = models.ForeignKey(
        Usuário,
        on_delete=models.SET_NULL,
        null=True,
        related_name="security_events",
    )
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAdicionarressField()
    user_agent = models.TextField(blank=True)
    description = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[
            ("low", "Baixo"),
            ("medium", "Médio"),
            ("high", "Alto"),
            ("critical", "Crítico"),
        ],
        default="medium",
    )
    is_resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Evento de Segurança"
        verbose_name_plural = "Eventos de Segurança"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} - {self.ip_address}"


# ============================================================================
# 5. AUDIT CONFIGURATION SUB-MODULE
# ============================================================================

class AuditoriaConfig(TenantAwareModel):
    """Auditoria configuration and policies."""

    retention_days = models.IntegerField(default=365)
    log_login_attempts = models.BooleanField(default=True)
    log_data_changes = models.BooleanField(default=True)
    log_exports = models.BooleanField(default=True)
    require_2fa = models.BooleanField(default=False)
    password_expiry_days = models.IntegerField(null=True, blank=True)
    max_failed_login_attempts = models.IntegerField(default=5)
    lockout_duration_minutes = models.IntegerField(default=15)

    class Meta:
        verbose_name = "Configuração de Auditoriaoria"
        verbose_name_plural = "Configurações de Auditoriaoria"

    def __str__(self):
        return f"Auditoria Config - {self.company.name}"
