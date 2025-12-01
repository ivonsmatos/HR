"""Finance app admin configuration."""
from django.contrib import admin
from .models import (
    Invoice, InvoiceItem, Estimate, Proposal, Expense,
    PaymentGateway, Payment
)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "client", "total_amount", "status", "due_date"]
    list_filter = ["company", "status", "issue_date"]
    search_fields = ["invoice_number", "client__name"]


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ["invoice", "description", "quantity", "unit_price", "amount"]
    list_filter = ["company", "invoice"]
    search_fields = ["invoice__invoice_number"]


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ["estimate_number", "client", "total_amount", "status"]
    list_filter = ["company", "status"]
    search_fields = ["estimate_number", "client__name"]


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ["proposal_number", "client", "title", "status"]
    list_filter = ["company", "status"]
    search_fields = ["proposal_number", "client__name"]


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ["employee", "category", "amount", "status"]
    list_filter = ["company", "category", "status"]
    search_fields = ["employee__username"]


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ["name", "company", "is_active"]
    list_filter = ["company", "is_active"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["transaction_id", "invoice", "amount", "status", "payment_date"]
    list_filter = ["company", "status", "payment_method"]
    search_fields = ["transaction_id", "invoice__invoice_number"]
