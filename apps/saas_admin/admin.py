"""SaaS Admin app admin configuration."""
from django.contrib import admin
from .models import SubscriptionPlan, Subscription, BillingInvoice, Coupon


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "billing_cycle", "max_users", "is_active"]
    list_filter = ["is_active", "billing_cycle"]
    search_fields = ["name"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["company", "plan", "status", "start_date", "renewal_date"]
    list_filter = ["status", "plan", "start_date"]
    search_fields = ["company__name"]


@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "subscription", "amount", "status", "due_date"]
    list_filter = ["status", "issued_date"]
    search_fields = ["invoice_number"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_value", "discount_type", "valid_until", "is_active"]
    list_filter = ["is_active", "discount_type"]
    search_fields = ["code"]
