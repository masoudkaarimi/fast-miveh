from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from apps.common.models import TimeStampedModel
from apps.common.utils import GenerateUploadPath
from apps.common.validators import FileExtensionValidator, FileSizeValidator
from apps.core.utils import get_provider_choices


class Currency(TimeStampedModel):
    """A model representing a currency used in the application."""
    code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name=_("Currency Code"),
        help_text=_("The ISO 4217 currency code, e.g., 'USD', 'EUR'.")
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("Currency Name"),
        help_text=_("The full name of the currency, e.g., 'United States Dollar'.")
    )
    symbol = models.CharField(
        max_length=10,
        verbose_name=_("Currency Symbol"),
        help_text=_("The symbol for the currency, e.g., '$', '€'.")
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=1.0,
        verbose_name=_("Exchange Rate"),
        help_text=_("The exchange rate is relative to the site's base currency.")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("controls active status. inactive items are hidden without being deleted.")
    )

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
        ordering = ['code']
        constraints = [
            models.CheckConstraint(
                check=Q(exchange_rate__gt=0),
                name='positive_currency_exchange_rate'
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class SiteConfiguration(SingletonModel, TimeStampedModel):
    """A model for storing site-wide configuration settings."""
    site_name = models.CharField(
        max_length=255,
        blank=True,
        default=_("Fast Miveh"),
        verbose_name=_("Site Name"),
        help_text=_("The official name of the site. (Optional)")
    )
    site_logo = models.FileField(
        upload_to=GenerateUploadPath(base_path='uploads/configuration/'),
        blank=True,
        null=True,
        validators=[
            FileSizeValidator(max_size_mb=settings.MAX_IMAGE_UPLOAD_SIZE_MB),
            FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)
        ],
        verbose_name=_("Site Logo"),
        help_text=_(
            'A logo image for the site.<br />'
            'Supported formats: <b>{allowed_image_extensions}</b>.<br />'
            'Maximum file size: <b>{max_size}MB</b>.'
        ).format(
            allowed_image_extensions=', '.join(settings.ALLOWED_IMAGE_EXTENSIONS),
            max_size=settings.MAX_IMAGE_UPLOAD_SIZE_MB
        )
    )
    default_currency = models.ForeignKey(
        "Currency",
        on_delete=models.PROTECT,
        related_name='+',
        null=True,
        blank=True,
        verbose_name=_("Default Currency"),
        help_text=_("The default currency used for displaying prices.")
    )
    # default_payment_gateway = models.ForeignKey(
    #     'payments.PaymentGateway',
    #     on_delete=models.PROTECT,
    #     related_name='+',
    #     verbose_name=_("Default Payment Gateway"),
    #     help_text=_("The payment gateway selected by default at checkout.")
    # )
    active_sms_provider = models.CharField(
        max_length=50,
        choices=get_provider_choices('sms'),
        default='console_sms',
        blank=True,
        verbose_name=_("Active SMS Provider"),
        help_text=_("The active SMS provider for the site.")
    )
    active_email_provider = models.CharField(
        max_length=50,
        choices=get_provider_choices('email'),
        default='django_email',
        blank=True,
        verbose_name=_("Active Email Provider"),
        help_text=_("The active email provider for the site.")
    )
    active_telegram_provider = models.CharField(
        max_length=50,
        choices=get_provider_choices('telegram'),
        default='telegram_bot',
        blank=True,
        verbose_name=_("Active Telegram Provider"),
    )
    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name=_("Maintenance Mode"),
        help_text=_("If checked, a maintenance page will be shown to all non-staff users.")
    )

    class Meta:
        verbose_name = _("Site Configuration")

    def __str__(self):
        return f"{self.site_name} Configuration"
