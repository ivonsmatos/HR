"""
TYPE HINTS ADDITIONS for apps/core/models.py

This file contains the enhanced type hints for the core models.
Merge these changes with the existing models.py
"""

from typing import Optional, Dict, Any, List, QuerySet, Type
from datetime import datetime
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

    id: models.BigAutoField = models.BigAutoField(primary_key=True)
    uuid: models.UUIDField = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    is_active: models.BooleanField = models.BooleanField(default=True, db_index=True)
    created_by: models.CharField = models.CharField(max_length=255, null=True, blank=True)
    updated_by: models.CharField = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def __repr__(self) -> str:
        """Return string representation"""
        return f"<{self.__class__.__name__}: {self.id}>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary"""
        return {
            "id": self.id,
            "uuid": str(self.uuid),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
        }


class TenantAwareModel(BaseModel):
    """
    Abstract model for all tenant-aware models.
    Ensures data isolation by company (tenant).
    """

    company: models.ForeignKey = models.ForeignKey(
        "core.Company",
        on_delete=models.CASCADE,
        related_name="%(class)s_company",
        help_text="Company (Tenant) this record belongs to",
    )

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to ensure company is set"""
        if not self.company_id and hasattr(self, "get_current_tenant"):
            self.company = self.get_current_tenant()
        super().save(*args, **kwargs)

    def get_company_slug(self) -> Optional[str]:
        """Get company slug if tenant is set"""
        return self.company.slug if self.company else None


class Company(TenantMixin, BaseModel):
    """
    Tenant (Company) model for multi-tenant SaaS application.
    Represents each organization using the platform.
    """

    name: models.CharField = models.CharField(
        max_length=255,
        unique=True,
        help_text="Company name",
    )
    slug: models.SlugField = models.SlugField(
        max_length=50,
        unique=True,
        help_text="Unique identifier for URL",
    )
    description: models.TextField = models.TextField(blank=True)
    
    # Contact Information
    email: models.EmailField = models.EmailField(help_text="Company primary email")
    phone: models.CharField = models.CharField(max_length=20, blank=True)
    website: models.URLField = models.URLField(blank=True)
    
    # Address
    address: models.CharField = models.CharField(max_length=255, blank=True)
    city: models.CharField = models.CharField(max_length=100, blank=True)
    state: models.CharField = models.CharField(max_length=100, blank=True)
    postal_code: models.CharField = models.CharField(max_length=20, blank=True)
    country: models.CharField = models.CharField(max_length=100, blank=True)
    
    # Organization Details
    industry: models.CharField = models.CharField(
        max_length=100,
        blank=True,
        help_text="Industry vertical",
    )
    company_size: models.CharField = models.CharField(
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
    currency: models.CharField = models.CharField(
        max_length=3,
        default="BRL",
    )
    timezone: models.CharField = models.CharField(
        max_length=50,
        default="America/Sao_Paulo",
    )
    
    # Logo & Branding
    logo: models.ImageField = models.ImageField(
        upload_to="company_logos/",
        null=True,
        blank=True,
    )
    
    # Subscription
    subscription_plan: models.ForeignKey = models.ForeignKey(
        "saas_admin.SubscriptionPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="companies",
    )
    subscription_status: models.CharField = models.CharField(
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
    trial_ends_at: Optional[models.DateTimeField] = models.DateTimeField(null=True, blank=True)
    subscription_ends_at: Optional[models.DateTimeField] = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_verified: models.BooleanField = models.BooleanField(default=False)
    is_on_trial: models.BooleanField = models.BooleanField(default=True)
    
    # Audit
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)
    deleted_at: Optional[models.DateTimeField] = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.slug})"

    def is_subscription_active(self) -> bool:
        """Check if subscription is currently active"""
        return self.subscription_status == "active" and (
            not self.subscription_ends_at or self.subscription_ends_at > datetime.now()
        )

    def get_users(self) -> QuerySet:
        """Get all active users for this company"""
        return self.users.filter(is_active=True)

    def get_user_count(self) -> int:
        """Get count of active users"""
        return self.get_users().count()


class CompanyDomain(DomainMixin):
    """
    Domain model for routing requests to correct tenant.
    Used by django-tenants to determine company's database schema.
    """

    company: models.OneToOneField = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name="domain",
    )

    class Meta:
        verbose_name = _("Company Domain")
        verbose_name_plural = _("Company Domains")

    def __str__(self) -> str:
        return f"{self.domain} -> {self.company.name}"


class User(AbstractUser):
    """
    Custom User model for the platform.
    Extends Django's AbstractUser to add custom fields.
    """

    # Tenant Reference
    company: Optional[models.ForeignKey] = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True,
    )

    # Profile Information
    avatar: models.ImageField = models.ImageField(
        upload_to="user_avatars/",
        null=True,
        blank=True,
    )
    phone: models.CharField = models.CharField(max_length=20, blank=True)
    bio: models.TextField = models.TextField(max_length=500, blank=True)
    
    # Department & Role
    department: models.CharField = models.CharField(max_length=100, blank=True)
    job_title: models.CharField = models.CharField(max_length=100, blank=True)
    
    # Authentication & Security
    is_verified: models.BooleanField = models.BooleanField(default=False)
    email_verified: models.BooleanField = models.BooleanField(default=False)
    email_verified_at: Optional[models.DateTimeField] = models.DateTimeField(null=True, blank=True)
    two_factor_enabled: models.BooleanField = models.BooleanField(default=False)
    
    # Status
    is_employee: models.BooleanField = models.BooleanField(default=False)
    is_contractor: models.BooleanField = models.BooleanField(default=False)
    
    # Preferences
    language: models.CharField = models.CharField(
        max_length=10,
        default="pt-br",
        choices=[
            ("pt-br", "Português (Brasil)"),
            ("en", "English"),
            ("es", "Español"),
        ],
    )
    timezone: models.CharField = models.CharField(max_length=50, default="America/Sao_Paulo")
    
    # Activity Tracking
    last_login_ip: Optional[models.GenericIPAddressField] = models.GenericIPAddressField(null=True, blank=True)
    last_activity: Optional[models.DateTimeField] = models.DateTimeField(null=True, blank=True)
    login_count: models.IntegerField = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.get_full_name()} ({self.username})"

    def get_full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def get_company(self) -> Optional["Company"]:
        """Get user's company"""
        return self.company

    def is_admin_user(self) -> bool:
        """Check if user is admin"""
        return self.is_staff or self.is_superuser

    def increment_login_count(self) -> None:
        """Increment login counter"""
        self.login_count += 1
        self.save(update_fields=["login_count", "last_activity"])

    def to_dict(self, include_company: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.get_full_name(),
            "phone": self.phone,
            "bio": self.bio,
            "department": self.department,
            "job_title": self.job_title,
            "is_verified": self.is_verified,
            "email_verified": self.email_verified,
            "two_factor_enabled": self.two_factor_enabled,
            "is_employee": self.is_employee,
            "is_contractor": self.is_contractor,
            "language": self.language,
            "timezone": self.timezone,
            "login_count": self.login_count,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }
        
        if include_company and self.company:
            data["company"] = {
                "id": self.company.id,
                "name": self.company.name,
                "slug": self.company.slug,
            }
        
        return data


class UserProfile(TenantAwareModel):
    """
    Extended user profile for additional user information.
    Tenant-aware for multi-tenant support.
    """

    user: models.OneToOneField = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Professional Info
    job_title_full: models.CharField = models.CharField(max_length=255, blank=True)
    department_full: models.CharField = models.CharField(max_length=255, blank=True)
    manager: Optional[models.ForeignKey] = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )
    
    # Dates
    hire_date: Optional[models.DateField] = models.DateField(null=True, blank=True)
    birth_date: Optional[models.DateField] = models.DateField(null=True, blank=True)
    
    # Additional Contact
    phone_personal: models.CharField = models.CharField(max_length=20, blank=True)
    address_personal: models.CharField = models.CharField(max_length=255, blank=True)
    
    # Preferences & Settings
    notification_email: models.BooleanField = models.BooleanField(default=True)
    notification_push: models.BooleanField = models.BooleanField(default=True)
    notification_sms: models.BooleanField = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Profile of {self.user.get_full_name()}"

    def get_manager_name(self) -> Optional[str]:
        """Get manager's name if assigned"""
        return self.manager.get_full_name() if self.manager else None

    def is_manager(self) -> bool:
        """Check if user has subordinates"""
        return self.subordinates.exists()

    def get_subordinates_count(self) -> int:
        """Get count of direct subordinates"""
        return self.subordinates.count()
