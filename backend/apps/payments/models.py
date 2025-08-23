import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.common.models import TimeStampedModel
from apps.common.utils import GenerateUploadPath
from apps.common.validators import FileExtensionValidator, FileSizeValidator


class PaymentGateway(TimeStampedModel):
    """
    Stores information about a payment gateway provider.
    e.g., Zarinpal, Stripe, PayPal.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Gateway Name"),
        help_text=_("The display name of the payment gateway, e.g., 'Zarinpal', 'Stripe'.")
    )
    identifier = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name=_("Identifier"),
        help_text=_("A unique identifier for the gateway's service class, e.g., 'zarinpal_gateway'.")
    )
    logo = models.FileField(
        upload_to=GenerateUploadPath(base_path='uploads/gateways/'),
        blank=True,
        null=True,
        validators=[
            FileSizeValidator(max_size_mb=settings.MAX_IMAGE_UPLOAD_SIZE_MB),
            FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)
        ],
        verbose_name=_("logo"),
        help_text=_(
            'A logo image for the gateway. (Optional)<br />'
            'Supported formats: <b>{allowed_image_extensions}</b>.<br />'
            'Maximum file size: <b>{max_size}MB</b>.'
        ).format(
            allowed_image_extensions=', '.join(settings.ALLOWED_IMAGE_EXTENSIONS),
            max_size=settings.MAX_IMAGE_UPLOAD_SIZE_MB
        ),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A short description or special conditions for the gateway, e.g., 'Requires a minimum purchase of 10,000 Tomans'.")
    )
    min_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
        verbose_name=_("Minimum Amount"),
        help_text=_("The minimum order amount required to use this gateway. Leave blank if there is no limit. (Optional)")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )
    supported_countries = CountryField(
        multiple=True,
        blank=True,
        verbose_name=_("Supported Countries"),
        help_text=_("Select the countries where this gateway is available. Leave blank to support all countries. (Optional)")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
    )

    class Meta:
        verbose_name = _("Payment Gateway")
        verbose_name_plural = _("Payment Gateways")
        ordering = ['display_order', 'name']
        constraints = [
            models.CheckConstraint(
                check=models.Q(min_amount__gte=0),
                name='non_negative_payment_gateway_min_amount'
            )
        ]

    def __str__(self):
        return self.name

    def get_supported_countries_list(self):
        """Returns a list of supported country codes."""
        return self.supported_countries if self.supported_countries else []


class PaymentTransaction(TimeStampedModel):
    """
    Records each payment transaction attempt made through a payment gateway.
    Uses GenericForeignKey to associate with any model (e.g., Order, Subscription).
    """

    class TransactionStatus(models.TextChoices):
        PENDING = 'pending', _("Pending")
        SUCCESSFUL = 'successful', _("Successful")
        FAILED = 'failed', _("Failed")
        REFUNDED = 'refunded', _("Refunded")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.PROTECT,
        verbose_name=_("Content Type"),
        help_text=_("The model to which this transaction is related.")
    )
    object_id = models.CharField(
        max_length=255,
        verbose_name=_("Object ID"),
        help_text=_("The primary key of the related object.")
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    gateway = models.ForeignKey(
        PaymentGateway,
        on_delete=models.PROTECT,
        related_name='transactions',
        verbose_name=_("Gateway"),
        help_text=_("The payment gateway used for this transaction.")
    )
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
        verbose_name=_("Status"),
        help_text=_("The current status of the transaction attempt.")
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("The amount that was processed in the transaction.")
    )
    currency = models.CharField(
        max_length=10,
        verbose_name=_("Currency Code"),
        help_text=_("The currency code for the transaction, e.g., 'TOMAN', 'USD'.")
    )
    gateway_token = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("Gateway Token"),
        help_text=_("A unique token from the gateway to identify the transaction before it's verified (e.g., authority).")
    )
    gateway_transaction_id = models.CharField(
        max_length=255,
        blank=True,
        db_index=True,
        verbose_name=_("Gateway Transaction ID"),
        help_text=_("The unique ID provided by the payment gateway for this transaction after verification (e.g., ref_id). (Optional)")
    )
    gateway_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Gateway Response"),
        help_text=_("A JSON field to store the full response from the gateway for debugging. (Optional)")
    )

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gte=0),
                name='non_negative_payment_transaction_amount'
            ),
            models.UniqueConstraint(
                fields=['gateway', 'gateway_transaction_id'],
                condition=Q(gateway_transaction_id__isnull=False) & ~Q(gateway_transaction_id=''),
                name='unique_non_empty_gateway_transaction_id'
            )
        ]

    def __str__(self):
        return f"Transaction {self.id} - {self.get_status_display()} for {self.content_object}"
