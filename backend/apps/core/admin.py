from django.contrib import admin
from solo.admin import SingletonModelAdmin

from apps.core.models import Currency, SiteConfiguration


@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(SingletonModelAdmin):
    fieldsets = (
        ('Site Info', {
            'fields': ('site_name', 'site_logo', 'maintenance_mode')
        }),
        ('Localization & Payments', {
            'fields': ('default_currency',)  # TODO: add default_payment_gateway when implemented
        }),
        ('Notification Settings', {
            'description': "Select the active providers for sending notifications.",
            'fields': ('active_sms_provider', 'active_email_provider')
        }),
    )


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'symbol', 'exchange_rate', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    list_editable = ('exchange_rate', 'is_active')
