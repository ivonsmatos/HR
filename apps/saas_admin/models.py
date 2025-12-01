"""
SAAS ADMIN (SaaS Administration) App Models

Sub-modules:
- SubscriptionPlans: Plan management
- Subscriptions: Customer subscriptions
- Billing: Billing and invoicing
- Coupons: Promotional codes
"""

from django.db import models
from apps.core.models import TenantAwareModel, BaseModel, User, Company


# ============================================================================
# 1. SUBSCRIPTION PLANS SUB-MODULE
# ============================================================================

class SubscriptionPlan(BaseModel):
    """SaaS subscription plans (not tenant-specific)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    billing_cycle = models.CharField(
        max_length=20,
        choices=[
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annual", "Annual"),
        ],
    )
    
    # Features
    max_users = models.IntegerField(null=True, blank=True, help_text="Max users per company, null=unlimited")
    max_storage_gb = models.IntegerField(null=True, blank=True, help_text="Max storage in GB, null=unlimited")
    
    # Modules/Features Included
    includes_hrm = models.BooleanField(default=False)
    includes_finance = models.BooleanField(default=False)
    includes_crm = models.BooleanField(default=False)
    includes_recruitment = models.BooleanField(default=False)
    includes_projects = models.BooleanField(default=False)
    includes_assets = models.BooleanField(default=False)
    
    # Support
    support_level = models.CharField(
        max_length=50,
        choices=[
            ("email", "Email Support"),
            ("priority", "Priority Support"),
            ("dedicated", "Dedicated Support"),
        ],
        default="email",
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"
        ordering = ["display_order"]

    def __str__(self):
        return f"{self.name} (${self.price}/{self.billing_cycle})"


# ============================================================================
# 2. SUBSCRIPTIONS SUB-MODULE
# ============================================================================

class Subscription(TenantAwareModel):
    """Customer subscriptions."""

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    
    # Dates
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    renewal_date = models.DateField()
    
    # Amount
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("trial", "Trial"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("cancelled", "Cancelled"),
            ("expired", "Expired"),
        ],
        default="trial",
    )
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=True)
    
    # Payment Gateway
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("stripe", "Stripe"),
            ("paypal", "PayPal"),
            ("razorpay", "Razorpay"),
        ],
        null=True,
        blank=True,
    )
    gateway_subscription_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self):
        return f"{self.company.name} - {self.plan.name}"


# ============================================================================
# 3. BILLING SUB-MODULE
# ============================================================================

class BillingInvoice(TenantAwareModel):
    """SaaS billing invoices (separate from Finance app invoices)."""

    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name="billing_invoices",
    )
    
    invoice_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Dates
    issued_date = models.DateField()
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("paid", "Paid"),
            ("overdue", "Overdue"),
        ],
        default="draft",
    )
    
    # Payment
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Billing Invoice"
        verbose_name_plural = "Billing Invoices"
        unique_together = ["company", "invoice_number"]

    def __str__(self):
        return f"Invoice {self.invoice_number}"


# ============================================================================
# 4. COUPONS SUB-MODULE
# ============================================================================

class Coupon(BaseModel):
    """Promotional coupons (not tenant-specific)."""

    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    # Discount
    discount_type = models.CharField(
        max_length=20,
        choices=[
            ("percentage", "Percentage"),
            ("fixed_amount", "Fixed Amount"),
        ],
    )
    discount_value = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Validity
    valid_from = models.DateField()
    valid_until = models.DateField()
    max_usage = models.IntegerField(null=True, blank=True, help_text="Maximum number of times coupon can be used")
    times_used = models.IntegerField(default=0)
    
    # Applicable Plans
    applicable_plans = models.ManyToManyField(
        SubscriptionPlan,
        blank=True,
        related_name="coupons",
    )
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"{self.code} ({self.discount_value})"
