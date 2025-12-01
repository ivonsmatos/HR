"""CRM app admin configuration."""
from django.contrib import admin
from .models import Client, Lead, Product, Order, OrderItem


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "status", "account_manager"]
    list_filter = ["company", "status", "industry"]
    search_fields = ["name", "email"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["name", "company_name", "stage", "source", "estimated_value"]
    list_filter = ["company", "stage", "source"]
    search_fields = ["name", "email", "company_name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "sku", "selling_price", "stock_quantity", "status"]
    list_filter = ["company", "category", "status"]
    search_fields = ["name", "sku"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "client", "total_amount", "status"]
    list_filter = ["company", "status", "order_date"]
    search_fields = ["order_number", "client__name"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "unit_price", "amount"]
    list_filter = ["company"]
    search_fields = ["order__order_number", "product__name"]
