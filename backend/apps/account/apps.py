from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.account"
    verbose_name = _("User Accounts")

    def ready(self):
        """Import signals when the app is ready."""
        import apps.account.signals
