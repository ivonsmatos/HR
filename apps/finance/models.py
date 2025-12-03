"""
FINANCE (Finance & Accounting) App Models

Sub-modules:
- Faturas: Invoice management and billing
- Estimates: Quotations and estimates
- Proposals: Business proposals
- Expenses: Expense tracking
- Payments: Payment processing and gateway integration
"""

from django.db import models
from apps.core.models import TenantAwareModel, Usuário


# ============================================================================
# 1. INVOICES SUB-MODULE
# ============================================================================

class Invoice(TenantAwareModel):
    """Client invoices."""

    invoice_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        "crm.Client",
        on_delete=models.PROTECT,
        related_name="invoices",
    )
    project = models.ForeignKey(
        "work.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices",
    )
    
    # Dates
    issue_date = models.DateField()
    due_date = models.DateField()
    
    # Amount
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Rascunho"),
            ("sent", "Enviado"),
            ("viewed", "Viewed"),
            ("partially_paid", "Partially Paid"),
            ("paid", "Pago"),
            ("overdue", "Vencido"),
            ("cancelled", "Cancelarado"),
        ],
        default="draft",
    )
    
    # Payment
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_terms = models.CharField(
        max_length=20,
        choices=[
            ("net_15", "Net 15"),
            ("net_30", "Net 30"),
            ("net_60", "Net 60"),
            ("custom", "Custom"),
        ],
        default="net_30",
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Fatura"
        verbose_name_plural = "Faturas"
        unique_together = ["company", "invoice_number"]

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class InvoiceItem(TenantAwareModel):
    """Invoice line items."""

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
    )
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=8, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Item da Fatura"
        verbose_name_plural = "Itens da Fatura"

    def __str__(self):
        return f"{self.description} (Invoice {self.invoice.invoice_number})"


# ============================================================================
# 2. ESTIMATES SUB-MODULE
# ============================================================================

class Estimate(TenantAwareModel):
    """Quotations/estimates."""

    estimate_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        "crm.Client",
        on_delete=models.CASCADE,
        related_name="estimates",
    )
    
    # Dates
    valid_until = models.DateField()
    
    # Amount
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Rascunho"),
            ("sent", "Enviado"),
            ("accepted", "Accepted"),
            ("rejected", "Rejeitado"),
            ("expired", "Expirado"),
        ],
        default="draft",
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"
        unique_together = ["company", "estimate_number"]

    def __str__(self):
        return f"Estimate {self.estimate_number}"


# ============================================================================
# 3. PROPOSALS SUB-MODULE
# ============================================================================

class Proposal(TenantAwareModel):
    """Business proposals."""

    proposal_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        "crm.Client",
        on_delete=models.CASCADE,
        related_name="proposals",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Dates
    valid_until = models.DateField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Rascunho"),
            ("sent", "Enviado"),
            ("accepted", "Accepted"),
            ("rejected", "Rejeitado"),
            ("expired", "Expirado"),
        ],
        default="draft",
    )
    proposed_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Proposta"
        verbose_name_plural = "Propostas"
        unique_together = ["company", "proposal_number"]

    def __str__(self):
        return f"Proposal {self.proposal_number}"


# ============================================================================
# 4. EXPENSES SUB-MODULE
# ============================================================================

class Expense(TenantAwareModel):
    """Employee expenses."""

    employee = models.ForeignKey(
        Usuário,
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    project = models.ForeignKey(
        "work.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expenses",
    )
    
    category = models.CharField(
        max_length=50,
        choices=[
            ("travel", "Travel"),
            ("meals", "Meals"),
            ("supplies", "Supplies"),
            ("software", "Software"),
            ("other", "Other"),
        ],
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    expense_date = models.DateField()
    
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Rascunho"),
            ("submitted", "Submitted"),
            ("approved", "Aprovado"),
            ("reimbursed", "Reimbursed"),
            ("rejected", "Rejeitado"),
        ],
        default="draft",
    )
    approved_by = models.ForeignKey(
        Usuário,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_expenses",
    )
    receipt = models.FileField(upload_to="expense_receipts/", null=True, blank=True)

    class Meta:
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"

    def __str__(self):
        return f"Expense {self.description} - ${self.amount}"


# ============================================================================
# 5. PAYMENTS SUB-MODULE
# ============================================================================

class PaymentGateway(TenantAwareModel):
    """Payment gateway configurations."""

    name = models.CharField(
        max_length=100,
        choices=[
            ("stripe", "Stripe"),
            ("paypal", "PayPal"),
            ("razorpay", "Razorpay"),
            ("mollie", "Mollie"),
            ("paystack", "Paystack"),
        ],
    )
    is_active = models.BooleanField(default=True)
    public_key = models.CharField(max_length=500)
    secret_key = models.CharField(max_length=500)
    webhook_url = models.URLField(blank=True)

    class Meta:
        verbose_name = "Gateway de Pagamento"
        verbose_name_plural = "Gateways de Pagamento"
        unique_together = ["company", "name"]

    def __str__(self):
        return f"{self.name} - {self.company.name}"


class Payment(TenantAwareModel):
    """Payment records."""

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments",
    )
    
    # Payment Details
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ("credit_card", "Credit Card"),
            ("debit_card", "Debit Card"),
            ("bank_transfer", "Bank Transfer"),
            ("check", "Check"),
            ("cash", "Cash"),
            ("other", "Other"),
        ],
    )
    
    # Transaction
    transaction_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pendente"),
            ("processing", "Processing"),
            ("completed", "Concluído"),
            ("failed", "Failed"),
            ("cancelled", "Cancelarado"),
        ],
        default="pending",
    )
    payment_date = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pagamento"
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        return f"Payment {self.transaction_id} - ${self.amount}"
