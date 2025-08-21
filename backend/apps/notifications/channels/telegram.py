import requests

from apps.notifications.channels.base import BaseNotificationChannel
from apps.notifications.exceptions import NotificationError


class TelegramBotChannel(BaseNotificationChannel):
    def __init__(self, **config):
        super().__init__(**config)
        self.telegram_bot_token = self.config.get('TELEGRAM_BOT_TOKEN')
        if not self.telegram_bot_token:
            raise NotificationError("Telegram 'TELEGRAM_BOT_TOKEN' is not configured in NOTIFICATIONS_SETTINGS.")
        self.api_url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"

    def send(self, recipient, **kwargs):
        message = kwargs.get('message', '')
        if not message:
            raise NotificationError("TelegramBotChannel requires a 'message' in kwargs.")

        payload = {
            'chat_id': recipient,
            'text': message,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()

            response_data = response.json()
            if not response_data.get('ok'):
                error_description = response_data.get('description', 'Unknown error')
                raise NotificationError(f"Telegram API Error: {error_description}")

        except requests.exceptions.RequestException as e:
            raise NotificationError(f"Failed to send message via Telegram Bot: {e}") from e
