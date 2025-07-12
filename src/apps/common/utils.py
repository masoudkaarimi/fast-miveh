import os
import string
import logging
import secrets
from typing import Any
from datetime import datetime, date

from django.conf import settings
from django.utils import timezone
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

import jdatetime

logger = logging.getLogger(__name__)


def is_admin(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name="admin").exists()


def is_superuser(user):
    return user.is_superuser and user.is_staff or user.groups.filter(name="superuser").exists()


def to_jalali(input_date, output_format='%Y-%m-%d'):
    if not input_date:
        return _("N/A")

    if isinstance(input_date, str):
        input_date = datetime.strptime(input_date, '%Y-%m-%d').date()
    elif isinstance(input_date, datetime):
        input_date = input_date.date()

    if not isinstance(input_date, date):
        raise ValueError("input_date must be a datetime, date, or string in 'YYYY-MM-DD' format")

    jalali_date = jdatetime.date.fromgregorian(date=input_date)

    return jalali_date.strftime(output_format)


def generate_numeric_otp(length: int = None) -> str:
    """
    Generates a secure numeric OTP.
    """
    length = length or settings.OTP_LENGTH
    if length < 4:
        raise ValueError("OTP length must be at least 4.")

    return "".join(secrets.choice(string.digits) for _ in range(length))


def get_remaining_time(target_time) -> str:
    if not target_time:
        return _("No target time set.")

    delta = target_time - timezone.now()
    total_seconds = delta.total_seconds()

    if total_seconds < 60:
        return f"{int(total_seconds)} seconds"

    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if delta.days:
        return f"{delta.days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    elif hours:
        return f"{hours} hours, {minutes} minutes, {seconds} seconds"
    else:
        return f"{minutes} minutes, {seconds} seconds"


# Todo: Make service
# def send_sms(message: str, phone: str, **kwargs) -> None:
#     # SMS Logic
#     logger.info("SMS sending is not implemented yet.")
#
#
# def send_email(subject: str, message: str, email: str, **kwargs) -> None:
#     send_mail(subject, message, from_email=settings.DEFAULT_FROM_EMAIL, recipient_list=[email], fail_silently=True, **kwargs)
#     logger.info("Email sent to %s", email)

def generate_upload_path(instance, filename, prefix='uploads', field_name=None):
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    extension = filename.rsplit('.', 1)[-1]

    if field_name:
        return f'{prefix}/{field_name}/{timestamp}.{extension}'

    return f'{prefix}/{timestamp}.{extension}'


@deconstructible
class GenerateUploadPath:
    def __init__(self, folder: str, sub_path: str) -> None:
        if not folder or not isinstance(folder, str):
            raise ValueError("Folder must be a non-empty string")
        if not sub_path or not isinstance(sub_path, str):
            raise ValueError("Sub-path must be a non-empty string")

        self.folder = folder
        self.sub_path = sub_path

    def __call__(self, instance: Any, filename: str) -> str:
        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        name, extension = os.path.splitext(filename)

        if not extension:
            raise ValueError("The uploaded file must have an extension")

        extension = extension.lower().strip(".")

        unique_id = secrets.token_hex(8)
        return f"{self.folder}/{self.sub_path}/{timestamp}_{unique_id}.{extension}"

    def __eq__(self, other):
        return (
                isinstance(other, GenerateUploadPath) and
                self.folder == other.folder and
                self.sub_path == other.sub_path
        )
