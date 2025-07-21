from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Custom user model manager where phone number is the unique identifier."""

    def _create_user(self, phone_number, password, **extra_fields):
        """
        Create and save a User with the given phone number and password.
        """
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))

        # A username is required, if not provided, use the phone number
        if 'username' not in extra_fields:
            extra_fields['username'] = str(phone_number)

        # Normalize the email if it exists
        if 'email' in extra_fields and extra_fields['email']:
            extra_fields['email'] = self.normalize_email(extra_fields['email'])

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        """Creates and saves a regular User."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password, **extra_fields):
        """Creates and saves a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_('Superuser must have is_staff=True.'))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(phone_number, password, **extra_fields)


class OTPManager(models.Manager):
    """Manager for the OTP model."""

    def create_otp(self, user, otp_type, recipient):
        from apps.account.utils import generate_numeric_otp

        # Deactivate previous OTPs for the same user, otp type, and recipient
        self.filter(
            user=user,
            otp_type=otp_type,
            recipient=recipient,
            status=self.model.StatusChoices.PENDING
        ).update(status=self.model.StatusChoices.EXPIRED)

        otp_code = generate_numeric_otp()
        otp_instance = self.create(user=user, code=otp_code, otp_type=otp_type, recipient=recipient)
        return otp_instance

    def get_latest_otp(self, user, otp_type, recipient):
        return self.filter(user=user, otp_type=otp_type, recipient=recipient).order_by('-created_at').first()
