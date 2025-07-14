import os
import secrets
import logging
from typing import Any, Union
from datetime import datetime, date

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext as _
from django.utils.deconstruct import deconstructible

import jdatetime

logger = logging.getLogger(__name__)


@deconstructible
class GenerateUploadPath:
    """
    A deconstructible class to generate a unique, timestamped upload path for files.
    Ensures that filenames are secure and do not collide.
    """

    def __init__(self, folder: str, sub_path: str = "") -> None:
        self.folder = folder
        self.sub_path = sub_path

    def __call__(self, instance: Any, filename: str) -> str:
        """
        Generates the file path.
        Example: `media/profiles/avatars/20250713_235859_a1b2c3d4e5f6a7b8.jpg`
        """
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")

        _, extension = os.path.splitext(filename)
        if not extension:
            extension = ""
        else:
            extension = extension[1:].lower()

        unique_id = secrets.token_hex(8)
        new_filename = f"{timestamp}_{unique_id}{'.' + extension if extension else ''}"

        return os.path.join(self.folder, self.sub_path, new_filename)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.folder == other.folder and self.sub_path == other.sub_path


def get_client_ip(request: Any) -> str:
    """A utility function to get the user's real IP address from a request, considering proxies and load balancers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_admin(user: settings.AUTH_USER_MODEL) -> bool:
    """Checks if a user has admin-level privileges."""
    return user.is_staff


def is_superuser(user: settings.AUTH_USER_MODEL) -> bool:
    """Checks if a user is a superuser."""
    return user.is_superuser


def to_jalali(gregorian_date: Union[datetime, date, str, None], output_format: str = '%Y/%m/%d') -> str:
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

# def get_remaining_time(target_time: datetime) -> str:
#     """Calculates the remaining time until a target datetime and returns a human-readable string."""
#     if not target_time or not isinstance(target_time, datetime):
#         return _("No target time set.")
#
#     now = timezone.now()
#     if target_time <= now:
#         return _("Expired")
#
#     delta: timedelta = target_time - now
#
#     days = delta.days
#     hours, remainder = divmod(delta.seconds, 3600)
#     minutes, seconds = divmod(remainder, 60)
#
#     parts = []
#     if days > 0:
#         parts.append(f"{days} " + (_("day") if days == 1 else _("days")))
#     if hours > 0:
#         parts.append(f"{hours} " + (_("hour") if hours == 1 else _("hours")))
#     if minutes > 0:
#         parts.append(f"{minutes} " + (_("minute") if minutes == 1 else _("minutes")))
#     if not parts:  # If less than a minute, show seconds
#         parts.append(f"{seconds} " + (_("second") if seconds == 1 else _("seconds")))
#
#     return ", ".join(parts)
