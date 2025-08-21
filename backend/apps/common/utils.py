import logging
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path

import jdatetime
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _

logger = logging.getLogger(__name__)


@deconstructible
class GenerateUploadPath:
    """
    A class to generate a unique, timestamped upload path for files.
    This approach ensures filenames are secure and do not collide.

    Usage in a model field:
        avatar = models.ImageField(upload_to=GenerateUploadPath(base_path="uploads/profiles/avatars/"))
    """

    def __init__(self, base_path):
        """
        Initializes the path generator.
        :param base_path: The base path where files will be stored (e.g., 'uploads/products/images/').
        """
        self.base_path = base_path

    def __call__(self, instance, filename):
        """
        Generates a secure file path when a file is uploaded.

        The final path format is:
        `{base_path}/{timestamp}_{unique_id}.{extension}`

        Example: `uploads/profiles/avatars/20250802_112539_a1b2c3d4.jpg`
        """
        extension = Path(filename).suffix.lower()
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        unique_id = secrets.token_hex(4)
        new_filename = f"{timestamp}_{unique_id}{extension}"
        path = Path(self.base_path) / new_filename

        return str(path)

    def __eq__(self, other):
        """
        This method is required by Django's migration framework to detect
        changes in the 'upload_to' attribute of a field.
        """
        return isinstance(other, self.__class__) and self.base_path == other.base_path


def get_client_ip(request):
    """A utility function to get the user's real IP address from a request, considering proxies and load balancers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_admin(user) -> bool:
    """Checks if a user has admin-level privileges."""
    return user.is_active and user.is_staff


def is_superuser(user) -> bool:
    """Checks if a user is a superuser."""
    return user.is_active and user.is_staff and user.is_superuser


def to_jalali(gregorian_date, output_format='%Y/%m/%d'):
    """Converts a Gregorian date (or datetime/string) to a formatted Jalali date string."""
    if not gregorian_date:
        return _("N/A")

    if isinstance(gregorian_date, str):
        try:
            gregorian_date = datetime.strptime(gregorian_date, '%Y-%m-%d').date()
        except ValueError:
            logger.warning(f"Invalid date string format for to_jalali: {gregorian_date}")
            return _("Invalid Date")
    elif isinstance(gregorian_date, datetime):
        gregorian_date = gregorian_date.date()

    if not isinstance(gregorian_date, date):
        logger.error(f"Unsupported type for to_jalali conversion: {type(gregorian_date)}")
        raise TypeError("Input must be a datetime, date, or string in 'YYYY-MM-DD' format")

    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
    return jalali_date.strftime(output_format)


def get_remaining_time(target_time):
    """Calculates the remaining time until a target datetime and returns a human-readable string."""
    if not target_time or not isinstance(target_time, datetime):
        return _("No target time set.")

    now = timezone.now()
    if target_time <= now:
        return _("Expired")

    delta = target_time - now

    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days} " + (_("day") if days == 1 else _("days")))
    if hours > 0:
        parts.append(f"{hours} " + (_("hour") if hours == 1 else _("hours")))
    if minutes > 0:
        parts.append(f"{minutes} " + (_("minute") if minutes == 1 else _("minutes")))
    if not parts:  # If less than a minute, show seconds
        parts.append(f"{seconds} " + (_("second") if seconds == 1 else _("seconds")))

    return ", ".join(parts)
