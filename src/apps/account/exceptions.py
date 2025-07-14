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
    pass
