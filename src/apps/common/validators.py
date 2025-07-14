import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator:
    """
    A class-based validator to check the file size.
    Made deconstructible to work with Django migrations.
    """

    def __init__(self, max_size_mb):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = self.max_size_mb * 1024 * 1024

    def __call__(self, value, serializer_field=None):
        """
        This method is called by the validation framework.
        'value' is the file object.
        'serializer_field' is an optional argument passed by DRF, which we ignore.
        """
        if value.size > self.max_size_bytes:
            max_size_mb_str = f'{self.max_size_mb:.2f}'
            raise ValidationError(
                _("File size cannot exceed %(max_size)s MB."),
                params={'max_size': max_size_mb_str}
            )

    def deconstruct(self):
        """Allows the validator to be serialized by migrations."""
        path = 'apps.common.validators.FileSizeValidator'
        args = (self.max_size_mb,)
        kwargs = {}
        return path, args, kwargs

    def __eq__(self, other):
        return (
                isinstance(other, self.__class__) and
                self.max_size_mb == other.max_size_mb
        )


@deconstructible
class FileExtensionValidator:
    """
    A class-based validator to check for allowed file extensions.
    Made deconstructible to work with Django migrations.
    """

    def __init__(self, allowed_extensions):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]

    def __call__(self, value, serializer_field=None):
        """
        Checks the file extension of the uploaded file.
        'serializer_field' is an optional argument passed by DRF, which we ignore.
        """
        # CORRECTED: Remove the leading dot from the extension before comparison
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
        return (
                isinstance(other, self.__class__) and
                self.allowed_extensions == other.allowed_extensions
        )
