from django.utils.translation import gettext_lazy as _


class OTPException(Exception):
    """Base exception for OTP operations."""
    default_message = _("An error occurred during the OTP process.")

    def __init__(self, message=None):
        if message is None:
            message = self.default_message
        super().__init__(message)


class OTPValidationError(OTPException):
    """Raised when OTP validation fails (invalid, expired, max attempts)."""
    default_message = _("The provided OTP is not valid.")


class OTPGenerationError(OTPException):
    """Raised when there's an issue generating or sending an OTP."""
    default_message = _("Could not generate or send the OTP code.")


class OTPCooldownError(OTPGenerationError):
    """Raised when trying to resend an OTP too quickly."""
    default_message = _("Please wait before requesting a new code.")

    def __init__(self, message=None, remaining_seconds=None):
        self.remaining_seconds = remaining_seconds
        # Pass the specific message to the base class constructor
        super().__init__(message)
