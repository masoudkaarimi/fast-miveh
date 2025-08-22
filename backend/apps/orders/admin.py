from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from apps.orders.models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'variant', 'quantity')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ('variant_link', 'product_title', 'variant_title', 'sku', 'quantity', 'unit_price', 'total_price')
    readonly_fields = fields
    extra = 0

    def variant_link(self, obj):
        if obj.variant:
            link = reverse("admin:products_productvariant_change", args=[obj.variant.pk])
            return format_html('<a href="{}" target="_blank">{}</a>', link, obj.variant)
        return f"{obj.product_title} ({obj.variant_title}) [Deleted]"

    variant_link.short_description = 'Product Variant'

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ('order_number', 'user_link', 'status', 'final_price', 'created_at',)
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__phone_number', 'user__username', 'shipping_address__full_name')
    ordering = ('-created_at',)
    readonly_fields = (
        'order_number', 'user_link', 'notes', 'shipping_address_link', 'billing_address_link', 'subtotal_price',
        'shipping_price', 'discount_amount', 'final_price', 'created_at', 'updated_at',
    )
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user_link', 'status', 'notes')
        }),
        ('Financials', {
            'fields': ('subtotal_price', 'shipping_price', 'discount_amount', 'final_price')
        }),
        ('Customer & Shipping', {
            'fields': ('shipping_address_link', 'billing_address_link')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def user_link(self, obj):
        link = reverse("admin:accounts_user_change", args=[obj.user.pk])
        return format_html('<a href="{}" target="_blank">{}</a>', link, obj.user)

    user_link.short_description = 'User'

    def shipping_address_link(self, obj):
        if obj.shipping_address:
            link = reverse("admin:accounts_address_change", args=[obj.shipping_address.pk])
            return format_html('<a href="{}" target="_blank">{}</a>', link, obj.shipping_address)
        return "-"

    shipping_address_link.short_description = 'Shipping Address'

    def billing_address_link(self, obj):
        if obj.billing_address:
            link = reverse("admin:accounts_address_change", args=[obj.billing_address.pk])
            return format_html('<a href="{}" target="_blank">{}</a>', link, obj.billing_address)
        return "-"

    billing_address_link.short_description = 'Billing Address'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.status not in [Order.OrderStatusChoices.SHIPPED, Order.OrderStatusChoices.DELIVERED, Order.OrderStatusChoices.CANCELLED, Order.OrderStatusChoices.REFUNDED]:
            if 'status' in readonly_fields:
                readonly_fields.remove('status')
        return readonly_fields
