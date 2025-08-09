from django.conf import settings
from django.utils.module_loading import import_string

from apps.core.models import SiteConfiguration
from apps.notification.exceptions import NotificationError


class NotificationService:
    def __init__(self):
        self.channels = self._load_channels()

    def _load_channels(self):
        loaded_channels = {}
        try:
            config = SiteConfiguration.get_solo()
            provider_map = settings.NOTIFICATION_PROVIDERS

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
        channel_class_path = provider_config['CHANNEL_CLASS']
        config_dict = provider_config.get('CONFIG', {})
        ChannelClass = import_string(channel_class_path)
        return ChannelClass(**config_dict)

    def send_email(self, recipient, **kwargs):
        if 'email' not in self.channels:
            raise NotificationError("No active email provider is configured in Site Configuration.")
        self.channels['email'].send(recipient, **kwargs)

    def send_sms(self, recipient, **kwargs):
        if 'sms' not in self.channels:
            raise NotificationError("No active SMS provider is configured in Site Configuration.")
        self.channels['sms'].send(recipient, **kwargs)

    def send_telegram(self, recipient, **kwargs):
        if 'telegram' not in self.channels:
            raise NotificationError("No active Telegram provider is configured in Site Configuration.")
        self.channels['telegram'].send(recipient, **kwargs)
