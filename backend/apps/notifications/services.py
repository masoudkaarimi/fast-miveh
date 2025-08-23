from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.module_loading import import_string

from apps.core.models import SiteConfiguration
from apps.notifications.exceptions import NotificationError
from apps.notifications.models import Notification


class NotificationService:
    """Service to manage user notifications."""

    def __init__(self, recipient):
        if not recipient:
            raise ValueError("A recipient user must be provided to the service.")
        self.recipient = recipient

    def create(self, *, title, body, category, related_object=None):
        """Creates a new notification for the recipient user."""
        params = {
            "recipient": self.recipient,
            "title": title,
            "body": body,
            "category": category,
        }

        if related_object:
            params["content_type"] = ContentType.objects.get_for_model(related_object)
            params["object_id"] = related_object.pk

        notification = Notification.objects.create(**params)
        return notification

    def mark_as_read(self, notification):
        """Marks a specific notification as read."""
        if notification.recipient == self.recipient:
            notification.mark_as_read()
            return True
        return False

    def mark_as_unread(self, notification):
        """Marks a specific notification as unread."""
        if notification.recipient == self.recipient:
            notification.mark_as_unread()
            return True
        return False

    def mark_all_as_read(self):
        """Marks all unread notifications for the recipient as read."""
        Notification.objects.unread_for_user(self.recipient).mark_all_as_read()


class NotificationChannelService:
    """Service to manage notification channels (Email, SMS, Telegram)."""

    def __init__(self):
        self.channels = self._load_channels()

    def _load_channels(self):
        loaded_channels = {}
        try:
            config = SiteConfiguration.get_solo()
            provider_map = settings.NOTIFICATION_SETTINGS.get('PROVIDERS', {})
            active_providers = [
                ('email', config.active_email_provider),
                ('sms', config.active_sms_provider),
                ('telegram', config.active_telegram_provider),
            ]
            for channel_key, provider in active_providers:
                if provider and provider in provider_map:
                    provider_config = provider_map[provider]
                    loaded_channels[channel_key] = self._initialize_channel(provider_config)
        except (KeyError, AttributeError) as e:
            raise NotificationError(f"Notification settings are misconfigured. Error: {e}") from e
        return loaded_channels

    @staticmethod
    def _initialize_channel(provider_config):
        class_path = provider_config['CLASS_PATH']
        config_dict = provider_config.get('CONFIG', {})
        ChannelClass = import_string(class_path)
        return ChannelClass(**config_dict)

    def send_email(self, recipient, **kwargs):
        if 'email' not in self.channels:
            raise NotificationError("No active email provider is configured.")
        self.channels['email'].send(recipient, **kwargs)

    def send_sms(self, recipient, **kwargs):
        if 'sms' not in self.channels:
            raise NotificationError("No active SMS provider is configured.")
        self.channels['sms'].send(recipient, **kwargs)

    def send_telegram(self, recipient, **kwargs):
        if 'telegram' not in self.channels:
            raise NotificationError("No active Telegram provider is configured.")
        self.channels['telegram'].send(recipient, **kwargs)
