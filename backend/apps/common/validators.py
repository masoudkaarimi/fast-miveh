import os

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileSizeValidator:
    """A class-based validator to check the file size."""

    def __init__(self, max_size_mb):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = self.max_size_mb * 1024 * 1024

    def __call__(self, value, serializer_field=None):
        if value.size > self.max_size_bytes:
            max_size_mb_str = f'{self.max_size_mb:.2f}'
            raise ValidationError(_("File size cannot exceed %(max_size)s MB."), params={'max_size': max_size_mb_str})

    def deconstruct(self):
        """Allows the validator to be serialized by migrations."""
        path = 'apps.common.validators.FileSizeValidator'
        args = (self.max_size_mb,)
        kwargs = {}
        return path, args, kwargs

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.max_size_mb == other.max_size_mb


@deconstructible
class FileExtensionValidator:
    """A class-based validator to check for allowed file extensions."""

    def __init__(self, allowed_extensions):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]

    def __call__(self, value, serializer_field=None):
        # Remove the leading dot from the extension before comparison
        ext = os.path.splitext(value.name)[1][1:].lower()
        if ext not in self.allowed_extensions:
            raise ValidationError(
                _("Unsupported file extension. Allowed extensions are: %(allowed_extensions)s"),
                params={'allowed_extensions': ', '.join(self.allowed_extensions)}
            )

    def deconstruct(self):
        """Allows the validator to be serialized by migrations."""
        path = 'apps.common.validators.FileExtensionValidator'
        args = (self.allowed_extensions,)
        kwargs = {}
        return path, args, kwargs

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.allowed_extensions == other.allowed_extensions
