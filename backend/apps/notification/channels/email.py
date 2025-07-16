from typing import Any

from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string

from apps.notification.exceptions import NotificationError
from apps.notification.channels.base import BaseNotificationChannel


class EmailChannel(BaseNotificationChannel):
    def send(self, recipient: str, **kwargs: Any) -> None:
        subject: str = kwargs.get('subject', 'Notification')
        message: str | None = kwargs.get('message')
        template_name: str | None = kwargs.get('template_name')
        context: dict[str, Any] = kwargs.get('context', {})

        if not template_name:
            raise NotificationError("EmailChannel requires a 'template_name' in kwargs.")

        try:
            from_email: str = str(self.config.get('FROM_EMAIL', ''))
            html_message: str = render_to_string(template_name, context)
            plain_message: str = strip_tags(message)

            send_mail(
                subject,
                plain_message,
                from_email,
                [recipient],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            raise NotificationError(f"Failed to send email via EmailChannel: {e}") from e
