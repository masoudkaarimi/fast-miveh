from django.utils.translation import gettext_lazy as _


class PaymentGatewayError(Exception):
    """Base exception for payment gateway operations."""
    default_message = _("An error occurred with the payment gateway.")

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        super().__init__(message)


class PaymentInitiationError(PaymentGatewayError):
    """Raised when payment initiation fails."""
    default_message = _("Failed to initiate the payment process.")


class PaymentVerificationError(PaymentGatewayError):
    """Raised when payment verification fails."""
    default_message = _("Failed to verify the payment.")


class PaymentGatewayNotFoundError(PaymentGatewayError):
    """Raised when a requested payment gateway is not found or is inactive."""
    default_message = _("The requested payment gateway is not available.")
