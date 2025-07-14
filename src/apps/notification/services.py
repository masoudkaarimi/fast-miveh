from typing import Any, Dict

from django.conf import settings
from django.utils.module_loading import import_string

from apps.notification.exceptions import NotificationError


class NotificationService:
    def __init__(self) -> None:
        self.channels: Dict[str, Any] = self._load_channels()

    def _load_channels(self) -> Dict[str, Any]:
        loaded_channels: Dict[str, Any] = {}
        try:
            # Load active Email channel
            email_provider_key: str = settings.NOTIFICATIONS_SETTINGS['ACTIVE_EMAIL_PROVIDER']
            email_config: Dict[str, Any] = settings.NOTIFICATIONS_SETTINGS['EMAIL_PROVIDERS'][email_provider_key]
            loaded_channels['email'] = self._initialize_channel(email_config)

            # Load active SMS channel
            sms_provider_key: str = settings.NOTIFICATIONS_SETTINGS['ACTIVE_SMS_PROVIDER']
            sms_config: Dict[str, Any] = settings.NOTIFICATIONS_SETTINGS['SMS_PROVIDERS'][sms_provider_key]
            loaded_channels['sms'] = self._initialize_channel(sms_config)

            # Load active Telegram channel
            telegram_provider_key: str = settings.NOTIFICATIONS_SETTINGS['ACTIVE_TELEGRAM_PROVIDER']
            telegram_config: Dict[str, Any] = settings.NOTIFICATIONS_SETTINGS['TELEGRAM_PROVIDERS'][telegram_provider_key]
            loaded_channels['telegram'] = self._initialize_channel(telegram_config)

        except (KeyError, AttributeError) as e:
            raise NotificationError(f"Notification settings are misconfigured. Error: {e}") from e

        return loaded_channels

    @staticmethod
    def _initialize_channel(provider_config: Dict[str, Any]) -> Any:
        channel_class_path: str = provider_config['CHANNEL_CLASS']
        config_dict: Dict[str, Any] = provider_config.get('CONFIG', {})
        ChannelClass: Any = import_string(channel_class_path)
        return ChannelClass(**config_dict)

    def send_email(self, recipient: str, **kwargs: Any) -> None:
        self.channels['email'].send(recipient, **kwargs)

    def send_sms(self, recipient: str, **kwargs: Any) -> None:
        self.channels['sms'].send(recipient, **kwargs)

    def send_telegram(self, recipient: str, **kwargs: Any) -> None:
        self.channels['telegram'].send(recipient, **kwargs)
