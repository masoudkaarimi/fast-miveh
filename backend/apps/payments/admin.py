from django.contrib import admin
from django.utils.html import format_html

from apps.payments.models import PaymentGateway, PaymentTransaction


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ('display_logo', 'name', 'identifier', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('name', 'identifier')
    prepopulated_fields = {'identifier': ('name',)}
    ordering = ('display_order',)

    def display_logo(self, obj):
        if obj.logo and obj.logo.url:
            return format_html('<img src="{}" width="25" height="25" />', obj.logo.url)
        return "N/A"

    display_logo.short_description = 'Logo'


@admin.register(PaymentTransaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'gateway', 'status', 'amount', 'currency', 'gateway_transaction_id', 'created_at')
    list_filter = ('status', 'gateway', 'created_at')
    search_fields = ('gateway_transaction_id',)
    ordering = ('-created_at',)
    readonly_fields = [f.name for f in PaymentTransaction._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
