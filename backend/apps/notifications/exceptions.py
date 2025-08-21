from django.utils.translation import gettext_lazy as _


class NotificationError(Exception):
    """Base exception for notification channel operations."""
    default_message = _("A notification could not be sent.")

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        super().__init__(message)
