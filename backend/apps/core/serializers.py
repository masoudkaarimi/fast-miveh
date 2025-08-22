from rest_framework import serializers
from django.templatetags.static import static

from apps.core.models import Currency, SiteConfiguration


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for the Currency model."""

    class Meta:
        model = Currency
        fields = ('id', 'code', 'name', 'symbol')


class SiteConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for the SiteConfiguration model, providing site-wide settings."""
    default_currency = CurrencySerializer(read_only=True)  # TODO: add default_payment_gateway when implemented
    site_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = SiteConfiguration
        fields = ('site_name', 'site_logo_url', 'default_currency', 'maintenance_mode',)

    def get_site_logo_url(self, obj):
        """Return the absolute URL for the site logo."""
        request = self.context.get('request')

        if obj.site_logo and hasattr(obj.site_logo, 'url'):
            return request.build_absolute_uri(obj.site_logo.url) if request else obj.site_logo.url

        placeholder_url = static('assets/images/placeholders/site_logo_placeholder.webp')
        return request.build_absolute_uri(placeholder_url) if request else placeholder_url
