"""
SAAS ADMIN (SaaS Administration) App Models

Sub-modules:
- SubscriptionPlanos: Plan management
- Assinaturas: Customer subscriptions
- Billing: Billing and invoicing
- Coupons: Promotional codes
"""

from django.db import models
from apps.core.models import TenantAwareModel, BaseModel, Usuário, Empresa


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
            ("monthly", "Mensal"),
            ("quarterly", "Quarterly"),
            ("annual", "Anual"),
        ],
    )
    
    # Recursos
    max_users = models.IntegerField(null=True, blank=True, help_text="Máximo de usuários por empresa, nulo=ilimitado")
    max_storage_gb = models.IntegerField(null=True, blank=True, help_text="Armazenamento máximo em GB, nulo=ilimitado")
    
    # Modules/Recursos Included
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
        verbose_name = "Plano de Assinatura"
        verbose_name_plural = "Planos de Assinatura"
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
            ("trial", "Teste"),
            ("active", "Ativo"),
            ("paused", "Pausado"),
            ("cancelled", "Cancelarado"),
            ("expired", "Expirado"),
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
        verbose_name = "Assinatura"
        verbose_name_plural = "Assinaturas"

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
            ("draft", "Rascunho"),
            ("sent", "Enviado"),
            ("paid", "Pago"),
            ("overdue", "Vencido"),
        ],
        default="draft",
    )
    
    # Payment
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Fatura de Cobrança"
        verbose_name_plural = "Faturas de Cobrança"
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
    max_usage = models.IntegerField(null=True, blank=True, help_text="Número máximo de vezes que o cupom pode ser usado")
    times_used = models.IntegerField(default=0)
    
    # Applicable Planos
    applicable_plans = models.ManyToManyField(
        SubscriptionPlan,
        blank=True,
        related_name="coupons",
    )
    
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Cupom"
        verbose_name_plural = "Cupons"

    def __str__(self):
        return f"{self.code} ({self.discount_value})"
