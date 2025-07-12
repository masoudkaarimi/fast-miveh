import datetime
from typing import Optional

from django.conf import settings
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.files.uploadedfile import UploadedFile


# from phonenumber_field.formfields import PhoneNumberField
# from phonenumber_field.phonenumber import PhoneNumber


@deconstructible
class FileSizeValidator:
    message = _("The maximum file size is “%(max_size)sMB”.")
    code = "invalid_file_size"

    def __init__(
            self,
            message: Optional[str] = None,
            code: Optional[str] = None,
            allowed_file_size: Optional[int] = None,
            allow_none: bool = False
    ) -> None:
        self.message = message or self.message
        self.code = code or self.code
        self.allowed_file_size = allowed_file_size * 1024 * 1024 if allowed_file_size is not None else settings.FILE_UPLOAD_MAX_MEMORY_SIZE
        self.allow_none = allow_none

    def __call__(self, value: Optional[UploadedFile]) -> None:
        if value is None:
            if not self.allow_none:
                raise ValidationError(
                    _("No file was uploaded."),
                    code='no_file'
                )
            else:
                return

        if value.size > self.allowed_file_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={'max_size': int(self.allowed_file_size / 1024 / 1024), "value": value}
            )

    def __eq__(self, other) -> bool:
        return (
                isinstance(other, FileSizeValidator) and
                self.message == other.message and
                self.code == other.code and
                self.allowed_file_size == other.allowed_file_size and
                self.allow_none == other.allow_none
        )


file_size_validator = FileSizeValidator()


@deconstructible
class PhoneNumberValidator:
    message = _("Enter a valid phone number.")
    code = "invalid_phone_number"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None, region: str = 'IR'):
        self.message = message or self.message
        self.code = code or self.code
        self.region = region

    def __call__(self, value: str):
        if not value:
            raise ValidationError(self.message, code=self.code, params={"value": value})

        # phone_number = PhoneNumber.from_string(phone_number=value, region=self.region)
        # if not PhoneNumberField().validate(phone_number):
        #     raise ValidationError(self.message, code=self.code, params={"value": value})

    def __eq__(self, other):
        return (
                isinstance(other, PhoneNumberValidator) and
                self.message == other.message and
                self.code == other.code and
                self.region == other.region
        )


phone_number_validator = PhoneNumberValidator()


def is_email(value: str) -> bool:
    try:
        validate_email(value)
        return True
    except ValidationError:
        return False


def is_phone_number(value: str, region: str = 'IR') -> bool:
    try:
        phone_number = PhoneNumber.from_string(phone_number=value, region=region)
        return phone_number.is_valid()
    except ValidationError:
        return False


@deconstructible
class BirthdateValidator:
    message = _("The birthdate cannot be in the future.")
    code = "invalid_birthdate"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None) -> None:
        self.message = message or self.message
        self.code = code or self.code

    def __call__(self, value):
        if value > datetime.date.today():
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other) -> bool:
        return (
                isinstance(other, BirthdateValidator) and
                self.message == other.message and
                self.code == other.code
        )


birthdate_validator = BirthdateValidator()
