from typing import Any

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.notifications.channels.base import BaseNotificationChannel
from apps.notifications.exceptions import NotificationError


class DjangoEmailChannel(BaseNotificationChannel):
    def send(self, recipient, **kwargs):
        subject = kwargs.get('subject', 'Notification')
        message = kwargs.get('message')
        template_name = kwargs.get('template_name')
        context = kwargs.get('context', {})

        if not template_name:
            raise NotificationError("EmailChannel requires a 'template_name' in kwargs.")

        try:
            from_email: str = str(self.config.get('FROM_EMAIL', ''))
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)

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
