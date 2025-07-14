import datetime

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class BirthdateValidator:
    """
    A class-based validator to ensure the birthdate is not in the future.
    Made deconstructible to work with Django migrations.
    """

    def __call__(self, value, serializer_field=None):
        """Checks the birthdate."""
        if value > datetime.date.today():
            raise ValidationError(_("The birthdate cannot be in the future."))


    def __eq__(self, other):
        return isinstance(other, self.__class__)
