from django.utils.translation import gettext_lazy as _


class CartError(Exception):
    """Base exception for cart-related errors."""
    default_message = _("An error occurred with the shopping cart.")

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        super().__init__(message)
