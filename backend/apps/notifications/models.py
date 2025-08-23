from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel
from apps.notifications.managers import NotificationManager

User = get_user_model()


class Notification(TimeStampedModel):
    """Represents a notification for a user in the system."""

    class Category(models.TextChoices):
        ORDERS = 'orders', _('Orders')
        PAYMENTS = 'payments', _('Payments')
        ACTIVITIES = 'activities', _('Activities')
        DISCOUNTS = 'discounts', _('Discounts')
        GENERAL = 'general', _('General')

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_("Recipient"),
        help_text=_("The user who will receive this notification.")
    )
    title = models.CharField(
        max_length=255,
        verbose_name=_("Title"),
        help_text=_("The title of the notification.")
    )
    body = models.TextField(
        verbose_name=_("Body"),
        help_text=_("The content of the notification. This can be a short message or a detailed description.")
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
        db_index=True,
        verbose_name=_("Category"),
        help_text=_("The category of the notification, used for filtering and organization.")
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Read"),
        help_text=_("Indicates whether the notification has been read by the recipient.")
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Read At"),
        help_text=_("The timestamp when the notification was read. Null if it has not been read yet.")
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Content Type"),
        help_text=_("The model to which this notification link is attached.")
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Object ID"),
        help_text=_("The primary key of the related object. (Optional)")
    )
    related_object = GenericForeignKey('content_type', 'object_id')

    objects = NotificationManager()

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.get_username()}: {self.title}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def mark_as_unread(self):
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])
