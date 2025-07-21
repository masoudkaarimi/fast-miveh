from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = _('Product Catalog')

    def ready(self):
        """Import signals when the app is ready."""
        import apps.products.signals
