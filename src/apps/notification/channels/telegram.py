from typing import Any

import requests

from apps.notification.exceptions import NotificationError
from apps.notification.channels.base import BaseNotificationChannel


class TelegramBotChannel(BaseNotificationChannel):
    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        self.bot_token: str | None = self.config.get('BOT_TOKEN')
        if not self.bot_token:
            raise NotificationError("Telegram 'BOT_TOKEN' is not configured in NOTIFICATIONS_SETTINGS.")
        self.api_url: str = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

    def send(self, recipient: str, **kwargs: Any) -> None:
        message: str = kwargs.get('message', '')
        if not message:
            raise NotificationError("TelegramBotChannel requires a 'message' in kwargs.")

        payload: dict[str, Any] = {
            'chat_id': recipient,
            'text': message,
            'parse_mode': 'Markdown'
        }

        try:
            response = requests.post(self.api_url, data=payload)
            response.raise_for_status()

            response_data: dict[str, Any] = response.json()
            if not response_data.get('ok'):
                error_description: str = response_data.get('description', 'Unknown error')
                raise NotificationError(f"Telegram API Error: {error_description}")

        except requests.exceptions.RequestException as e:
            raise NotificationError(f"Failed to send message via Telegram Bot: {e}") from e
