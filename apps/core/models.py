"""
Abstract base models for multi-tenant architecture.

These models provide the foundation for all tenant-aware models in the system.
All models that need to be isolated by tenant should inherit from TenantAwareModel.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django_tenants.models import TenantMixin, DomainMixin
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
        "core.Company",
        on_delete=models.CASCADE,
        related_name="%(class)s_company",
        help_text="Company (Tenant) this record belongs to",
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save to ensure company is set (if not already set)."""
        if not self.company_id and hasattr(self, "get_current_tenant"):
            self.company = self.get_current_tenant()
        super().save(*args, **kwargs)


class Company(TenantMixin, BaseModel):
    """
    Tenant (Company) model for multi-tenant SaaS application.
    
    Represents each organization using the platform.
    Each company has isolated data via schema isolation (django-tenants).
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Company name",
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for URL (e.g., acme-corp)",
    )
    description = models.TextField(blank=True, help_text="Company description")
    
    # Contact Information
    email = models.EmailField(help_text="Company primary email")
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Address
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Organization Details
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry vertical (e.g., Technology, Healthcare, Finance)",
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
        help_text="Default currency code (ISO 4217)",
    )
    timezone = models.CharField(
        max_length=50,
        default="America/Sao_Paulo",
        help_text="Company timezone",
    )
    
    # Logo & Branding
    logo = models.ImageField(
        upload_to="company_logos/",
        null=True,
        blank=True,
        help_text="Company logo",
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
            ("trial", "Trial"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("cancelled", "Cancelled"),
            ("expired", "Expired"),
        ],
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    subscription_ends_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    is_on_trial = models.BooleanField(default=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.slug})"


class CompanyDomain(DomainMixin):
    """
    Domain model for routing requests to correct tenant.
    
    Used by django-tenants to determine which company's database
    schema should be used based on the request domain.
    """

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="domain",
    )

    class Meta:
        verbose_name = _("Company Domain")
        verbose_name_plural = _("Company Domains")

    def __str__(self):
        return f"{self.domain} -> {self.company.name}"


class User(AbstractUser):
    """
    Custom User model for the platform.
    
    Extends Django's AbstractUser to add custom fields and tenant awareness.
    """

    # Tenant Reference
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
        help_text="Company this user belongs to",
    )

    # Profile Information
    avatar = models.ImageField(
        upload_to="user_avatars/",
        null=True,
        blank=True,
    )
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Department & Role (for HRM)
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
        verbose_name = _("User")
        verbose_name_plural = _("Users")
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


class UserPermission(TenantAwareModel):
    """
    Custom permission model for granular access control.
    
    Allows assigning specific permissions to users or roles
    within a tenant (company).
    """

    PERMISSION_LEVELS = [
        ("view", "View Only"),
        ("create", "Create"),
        ("edit", "Edit"),
        ("delete", "Delete"),
        ("export", "Export"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="custom_permissions",
    )
    module = models.CharField(
        max_length=50,
        choices=[
            ("employees", "Employees"),
            ("leaves", "Leaves"),
            ("attendance", "Attendance"),
            ("payroll", "Payroll"),
            ("performance", "Performance"),
            ("projects", "Projects"),
            ("tasks", "Tasks"),
            ("timelogs", "Time Logs"),
            ("finance", "Finance"),
            ("crm", "CRM"),
            ("recruitment", "Recruitment"),
            ("assets", "Assets"),
            ("tickets", "Tickets"),
        ],
    )
    permission_level = models.CharField(max_length=20, choices=PERMISSION_LEVELS)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("User Permission")
        verbose_name_plural = _("User Permissions")
        unique_together = ["company", "user", "module"]

    def __str__(self):
        return f"{self.user.username} - {self.module} ({self.permission_level})"


class AuditLog(TenantAwareModel):
    """
    Audit logging model for security and compliance.
    
    Records all significant actions performed by users for auditing
    and compliance purposes.
    """

    ACTION_CHOICES = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("export", "Export"),
        ("import", "Import"),
        ("download", "Download"),
        ("permission_change", "Permission Change"),
        ("config_change", "Configuration Change"),
    ]

    user = models.ForeignKey(
        User,
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
        verbose_name = _("Audit Log")
        verbose_name_plural = _("Audit Logs")
        indexes = [
            models.Index(fields=["company", "-created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} on {self.object_type} ({self.created_at})"
