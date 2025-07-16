import string
import secrets

from django.conf import settings
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField


def get_identifier_info(identifier_string):
    """Determines if an identifier is an email or phone number and returns its type and normalized value."""
    if not identifier_string:
        raise ValidationError(_("Identifier cannot be empty."))

    if '@' in identifier_string:
        try:
            validate_email(identifier_string)
            return 'email', identifier_string
        except ValidationError:
            raise ValidationError(_("Enter a valid email address."))
    else:
        try:
            phone_number_field = PhoneNumberField()
            normalized_phone = phone_number_field.to_internal_value(identifier_string)
            return 'phone_number', normalized_phone
        except ValidationError:
            raise ValidationError(_("Enter a valid phone number."))


def generate_numeric_otp(length: int = 6) -> str:
    """Generates a secure, numeric-only One-Time Password."""

    # Fallback to default length if setting is missing or invalid
    otp_length = settings.OTP_SETTINGS.get('OTP_LENGTH', length)
    if not isinstance(otp_length, int) or otp_length <= 0:
        otp_length = length

    return "".join(secrets.choice(string.digits) for _ in range(otp_length))
