"""
CRM (Customer Relationship Management) App Models

Sub-modules:
- Clients: Client/company records
- Leads: Lead management and pipeline
- Products: Product/service catalog
- Orders: Sales orders
"""

from django.db import models
from apps.core.models import TenantAwareModel, User


# ============================================================================
# 1. CLIENTS SUB-MODULE
# ============================================================================

class Client(TenantAwareModel):
    """Client records."""

    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    
    # Contact Person
    contact_person_name = models.CharField(max_length=255, blank=True)
    contact_person_email = models.EmailField(blank=True)
    contact_person_phone = models.CharField(max_length=20, blank=True)
    
    # Address
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Business Details
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    
    # Assignment
    account_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="clients",
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("prospect", "Perspectiva"),
            ("qualified", "Qualificado"),
            ("active", "Ativo"),
            ("inactive", "Inativo"),
            ("blocked", "Bloqueado"),
        ],
        default="prospect",
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        unique_together = ["company", "email"]

    def __str__(self):
        return self.name


# ============================================================================
# 2. LEADS SUB-MODULE
# ============================================================================

class Lead(TenantAwareModel):
    """Sales leads."""

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255)
    
    # Lead Source
    source = models.CharField(
        max_length=50,
        choices=[
            ("website", "Website"),
            ("referral", "Referral"),
            ("cold_call", "Cold Call"),
            ("email", "Email"),
            ("social_media", "Social Media"),
            ("event", "Evento"),
            ("other", "Other"),
        ],
    )
    
    # Pipeline
    stage = models.CharField(
        max_length=50,
        choices=[
            ("new", "Novo"),
            ("contacted", "Contacted"),
            ("qualified", "Qualificado"),
            ("proposal", "Proposal Sent"),
            ("negotiation", "Negociação"),
            ("closed_won", "Closed Won"),
            ("closed_lost", "Closed Lost"),
        ],
        default="new",
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )
    
    # Value
    estimated_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    probability = models.IntegerField(default=50, help_text="Probabilidade de fechamento %")
    
    # Dates
    follow_up_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Lead/Oportunidade"
        verbose_name_plural = "Leads/Oportunidades"

    def __str__(self):
        return f"{self.name} ({self.company_name})"


# ============================================================================
# 3. PRODUCTS SUB-MODULE
# ============================================================================

class Product(TenantAwareModel):
    """Products/services catalog."""

    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Pricing
    cost_price = models.DecimalField(max_digits=12, decimal_places=2)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    # Categorization
    category = models.CharField(
        max_length=100,
        choices=[
            ("service", "Service"),
            ("product", "Produto"),
            ("subscription", "Assinatura"),
            ("license", "License"),
        ],
    )
    
    # Stock
    stock_quantity = models.IntegerField(default=0)
    low_stock_alert = models.IntegerField(default=10)
    
    # Tax
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ("active", "Ativo"),
            ("inactive", "Inativo"),
            ("discontinued", "Discontinued"),
        ],
        default="active",
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        unique_together = ["company", "sku"]

    def __str__(self):
        return self.name


# ============================================================================
# 4. ORDERS SUB-MODULE
# ============================================================================

class Order(TenantAwareModel):
    """Sales orders."""

    order_number = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="orders",
    )
    
    # Dates
    order_date = models.DateField(auto_now_add=True)
    expected_delivery = models.DateField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Rascunho"),
            ("confirmed", "Confirmed"),
            ("processing", "Processing"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelado"),
        ],
        default="draft",
    )
    
    # Amount
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="BRL")
    
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        unique_together = ["company", "order_number"]

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(TenantAwareModel):
    """Order line items."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="order_items",
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens do Pedido"

    def __str__(self):
        return f"{self.product.name} (Order {self.order.order_number})"
