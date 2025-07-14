from typing import Any

from apps.notification.exceptions import NotificationError
from apps.notification.channels.base import BaseNotificationChannel


class ConsoleSMSChannel(BaseNotificationChannel):
    def send(self, recipient: str, **kwargs: Any) -> None:
        message: str = kwargs.get('message', '')
        print("--- CONSOLE SMS ---")
        print(f"To: {recipient}")
        print(f"Message: {message}")
        print("-------------------")


class TwilioSMSChannel(BaseNotificationChannel):
    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        try:
            from twilio.rest import Client
        except ImportError:
            raise ImportError("Twilio package is not installed. Run 'pip install twilio'.")

        self.account_sid: str | None = self.config.get('ACCOUNT_SID')
        self.auth_token: str | None = self.config.get('AUTH_TOKEN')
        self.from_number: str | None = self.config.get('FROM_NUMBER')

        if not all([self.account_sid, self.auth_token, self.from_number]):
            raise NotificationError("Twilio settings (ACCOUNT_SID, AUTH_TOKEN, FROM_NUMBER) are not configured.")

        self.client = Client(self.account_sid, self.auth_token)

    def send(self, recipient: str, **kwargs: Any) -> None:
        message: str = kwargs.get('message', '')
        if not message:
            raise NotificationError("TwilioSMSChannel requires a 'message' in kwargs.")
        try:
            self.client.messages.create(body=message, from_=self.from_number, to=recipient)
        except Exception as e:
            raise NotificationError(f"Failed to send SMS via Twilio: {e}") from e


class KavenegarSMSChannel(BaseNotificationChannel):
    def __init__(self, **config: Any) -> None:
        super().__init__(**config)
        try:
            from kavenegar import KavenegarAPI
        except ImportError:
            raise ImportError("Kavenegar package is not installed. Run 'pip install kavenegar'.")

        self.api_key: str | None = self.config.get('API_KEY')
        if not self.api_key:
            raise NotificationError("Kavenegar 'API_KEY' is not configured.")

        self.api = KavenegarAPI(self.api_key)

    def send(self, recipient: str, **kwargs: Any) -> None:
        message: str = kwargs.get('message', '')
        if not message:
            raise NotificationError("KavenegarSMSChannel requires a 'message' in kwargs.")
        try:
            params: dict[str, Any] = {'receptor': recipient, 'message': message}
            self.api.sms_send(params)
        except Exception as e:
            raise NotificationError(f"Failed to send SMS via Kavenegar: {e}") from e
