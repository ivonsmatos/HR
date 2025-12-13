"""
Abstract base models for multi-tenant architecture.

These models provide the foundation for all tenant-aware models in the system.
All models that need to be isolated by tenant should inherit from TenantAwareModel.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
# from django_tenants.models import TenantMixin, DomainMixin  # Disabled for Django 5.1 compatibility
import uuid


class BaseModel(models.Model):
    """
    Abstract base model with common fields for all models.
    Provides audit trail and common metadata.
    """

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class TenantAwareModel(BaseModel):
    """
    Abstract model for all tenant-aware models.
    Ensures data isolation by company (tenant).
    
    All business logic models should inherit from this model
    to automatically get tenant isolation.
    """

    company = models.ForeignKey(
        "core.Empresa",
        on_delete=models.CASCADE,
        related_name="%(class)s_company",
        help_text="Empresa (Tenant) a qual este registro pertence",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save to ensure company is set (if not already set)."""
        if not self.company_id and hasattr(self, "get_current_tenant"):
            self.company = self.get_current_tenant()
        super().save(*args, **kwargs)


# Commented out - django_tenants not compatible with Django 5.1
# class Empresa(TenantMixin, BaseModel):
#     """
#     Tenant (Empresa) model for multi-tenant SaaS application.
#     
#     Represents each organization using the platform.
#     Each company has isolated data via schema isolation (django-tenants).
#     """

class Empresa(BaseModel):
    """
    Empresa (Organization) model for SaaS application.
    
    Represents each organization using the platform.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nãome da Empresa",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Identificador único para URL (ex: acme-corp)",
    )
    description = models.TextField(blank=True, help_text="Descrição da Empresa")
    
    # Contact Informaçãormation
    email = models.EmailField(help_text="E-mail principal da empresa")
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Adicionarress
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Organization Details
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Vertical da indústria (ex: Tecnologia, Saúde, Finanças)",
    )
    company_size = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ("1-10", "1-10 employees"),
            ("11-50", "11-50 employees"),
            ("51-200", "51-200 employees"),
            ("201-500", "201-500 employees"),
            ("500+", "500+ employees"),
        ],
    )
    
    # Financial & Subscription
    currency = models.CharField(
        max_length=3,
        default="BRL",
        help_text="Código de moeda padrão (ISO 4217)",
    )
    timezone = models.CharField(
        max_length=50,
        default="America/Sao_Paulo",
        help_text="Fuso horário da empresa",
    )
    
    # Logo & Branding
    logo = models.ImageField(
        upload_to="company_logos/",
        null=True,
        blank=True,
        help_text="Logo da empresa",
    )
    
    # Subscription Plan (reference to SaaS plan)
    subscription_plan = models.ForeignKey(
        "saas_admin.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )
    subscription_status = models.CharField(
        max_length=20,
        default="active",
        choices=[
            ("trial", "Teste"),
            ("active", "Ativo"),
            ("paused", "Pausado"),
            ("cancelled", "Cancelarado"),
            ("expired", "Expirado"),
        ],
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_on_trial = models.BooleanField(default=True)
    
    # Auditoria
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Empresa")
        verbose_name_plural = _("Empresas")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.slug})"


class EmpresaDomain(models.Model):
    """
    Domain model for routing requests to correct tenant (Empresa).
    
    Associates domain names with companies for multi-tenant routing.
    Each company can have one or more domains.
    """

    company = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="domains",
        help_text="A empresa a qual este domínio pertence"
    )
    
    domain = models.CharField(
        max_length=253,
        unique=True,
        help_text="Nãome de domínio (ex: tenant.example.com)"
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Este é o domínio primário da empresa?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Empresa Domain")
        verbose_name_plural = _("Domínios da Empresa")
        unique_together = [['company', 'is_primary']]

    def __str__(self):
        return f"{self.domain} ({self.company.name})"


class Usuário(AbstractUser):
    """
    Custom Usuário model for the platform.
    
    Extends Django's AbstractUsuário to add custom fields and tenant awareness.
    """

    # Tenant Reference
    company = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        help_text="Empresa a qual este usuário pertence",
    )

    # Perfil Informaçãormation
    avatar = models.ImageField(
        upload_to="user_avatars/",
        null=True,
        blank=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Department & Papel (for HRM)
    department = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    
    # Authentication & Security
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)
    
    # Status
    is_employee = models.BooleanField(default=False)
    is_contractor = models.BooleanField(default=False)
    
    # Preferences
    language = models.CharField(
        max_length=10,
        default="pt-br",
        choices=[
            ("pt-br", "Português (Brasil)"),
            ("en", "English"),
            ("es", "Español"),
        ],
    )
    timezone = models.CharField(max_length=50, default="America/Sao_Paulo")
    
    # Activity Tracking
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    login_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")
        ordering = ["-date_joined"]
        unique_together = [("email", "company")]

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.company})"

    def get_full_name(self):
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return user's short name."""
        return self.first_name or self.username


# User class for AUTH_USER_MODEL = "core.User"
# This is the primary user model for the application
class User(Usuário):
    """
    User model for Django authentication.
    This class extends Usuário for compatibility with AUTH_USER_MODEL.
    """
    class Meta:
        proxy = True
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class UsuárioPermission(TenantAwareModel):
    """
    Custom permission model for granular access control.
    
    Allows assigning specific permissions to users or roles
    within a tenant (company).
    """

    PERMISSION_LEVELS = [
        ("view", "View Only"),
        ("create", "Create"),
        ("edit", "Editar"),
        ("delete", "Deletar"),
        ("export", "Exportar"),
    ]

    user = models.ForeignKey(
        Usuário,
        on_delete=models.CASCADE,
        related_name="custom_permissions",
    )
    module = models.CharField(
        max_length=50,
        choices=[
            ("employees", "Funcionários"),
            ("leaves", "Licenças/Férias"),
            ("attendance", "Frequência"),
            ("payroll", "Payroll"),
            ("performance", "Performance"),
            ("projects", "Projetos"),
            ("tasks", "Tarefas"),
            ("timelogs", "Registros de Tempo"),
            ("finance", "Finance"),
            ("crm", "CRM"),
            ("recruitment", "Recruitment"),
            ("assets", "Ativos/Bens"),
            ("tickets", "Tickets/Chamados"),
        ],
    )
    permission_level = models.CharField(max_length=20, choices=PERMISSION_LEVELS)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Usuário Permission")
        verbose_name_plural = _("Permissões do Usuário")
        unique_together = ["company", "user", "module"]

    def __str__(self):
        return f"{self.user.username} - {self.module} ({self.permission_level})"


class AuditoriaLog(TenantAwareModel):
    """
    Auditoria logging model for security and compliance.
    
    Records all significant actions performed by users for auditing
    and compliance purposes.
    """

    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Deletar"),
        ("login", "Entrar"),
        ("logout", "Sair"),
        ("export", "Exportar"),
        ("import", "Importar"),
        ("download", "Download"),
        ("permission_change", "Mudança de Permissão"),
        ("config_change", "Configuração Alterar"),
    ]

    user = models.ForeignKey(
        Usuário,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    module = models.CharField(max_length=50)
    object_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255)
    changes = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Auditoria Log")
        verbose_name_plural = _("Logs de Auditoriaoria")
        indexes = [
            models.Index(fields=["company", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} on {self.object_type} ({self.created_at})"
