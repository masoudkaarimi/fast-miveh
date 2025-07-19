class OTPException(Exception):
    """Base exception for OTP operations."""
    pass


class OTPValidationError(OTPException):
    """Raised when OTP validation fails (invalid, expired, max attempts)."""
    pass


class OTPGenerationError(OTPException):
    """Raised when there's an issue generating or sending an OTP."""
    pass


class OTPCooldownError(OTPGenerationError):
    """Raised when trying to resend an OTP too quickly."""

    def __init__(self, message, remaining_seconds=None):
        self.remaining_seconds = remaining_seconds
        super().__init__(message)

# class OTPCooldownError(OTPGenerationError):
#     pass
