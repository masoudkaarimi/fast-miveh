import secrets
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator

from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField

from apps.common.models import TimeStampedModel
from apps.common.utils import GenerateUploadPath
from apps.account.validators import BirthdateValidator
from apps.account.managers import OTPManager, UserManager
from apps.common.validators import FileSizeValidator, FileExtensionValidator

username_validator = UnicodeUsernameValidator()


class User(AbstractUser, TimeStampedModel):
    phone_number = PhoneNumberField(
        unique=True,
        verbose_name=_('Phone Number'),
        help_text=_("Required. The primary identifier for login and registration.")
    )
    is_phone_number_verified = models.BooleanField(
        default=False,
        verbose_name=_("Phone Number Verified"),
        help_text=_("Indicates if the user has verified their phone number via OTP.")
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Email Address"),
        help_text=_("Optional. Used for notifications and password recovery if verified.")
    )
    is_email_verified = models.BooleanField(
        default=False,
        verbose_name=_("Email Verified"),
        help_text=_("Indicates if the user has verified their email address.")
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name=_("Username"),
        help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages={"unique": _("A user with that username already exists.")},
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("Active Status"),
        help_text=_("Designates whether this user should be treated as active. Unselect this instead of deleting accounts."),
    )
    last_login_ip = models.GenericIPAddressField(verbose_name=_("Last Login IP"), blank=True, null=True)
    last_login_at = models.DateTimeField(verbose_name=_("Last Login Date"), blank=True, null=True)

    # --- Disabled Inherited Fields ---
    date_joined = None
    last_login = None

    # --- Manager and Field Configuration ---
    objects = UserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ['-created_at']

    def __str__(self):
        return str(self.phone_number)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def _anonymize_data(self):
        """Internal method to scramble PII and free up unique identifiers."""
        anonymized_prefix = f"deleted_{self.pk}"
        self.username = f"{anonymized_prefix}_{secrets.token_hex(4)}"
        self.email = None
        self.phone_number = f"_{anonymized_prefix}"
        self.first_name = ""
        self.last_name = ""
        self.is_email_verified = False
        self.is_phone_number_verified = False
        self.set_unusable_password()
        if hasattr(self, 'profile') and self.profile.avatar:
            self.profile.avatar.delete(save=False)

    def delete_account(self, permanent=False):
        """Deletes or deactivates and anonymizes the user account."""
        if permanent:
            return self.delete()
        else:
            self.is_active = False
            self._anonymize_data()
            self.save()
            return True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """A simple method to send an email to the user."""
        from apps.notification.services import NotificationService
        if self.email:
            NotificationService().send_email(recipient=self.email, subject=subject, message=message, from_email=from_email, **kwargs)

    def sms_user(self, message, **kwargs):
        """A simple method to send an SMS to the user."""
        from apps.notification.services import NotificationService
        if self.phone_number:
            NotificationService().send_sms(recipient=str(self.phone_number), message=message, **kwargs)


class Profile(TimeStampedModel):
    class GenderChoices(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer Not To Say')

    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User")
    )
    avatar = models.ImageField(
        upload_to=GenerateUploadPath('profiles', 'avatars'),
        default=None,
        blank=True,
        null=True,
        validators=[
            FileSizeValidator(max_size_mb=settings.MAX_IMAGE_UPLOAD_SIZE_MB),
            FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)
        ],
        verbose_name=_("Avatar"),
        help_text=_(
            'The user\'s avatar. (Optional)<br />'
            'Recommended size: <b>256x256px</b>.<br />'
            'Supported formats: <b>{allowed_image_extensions}</b>.<br />'
            'Maximum file size: <b>{max_size}MB</b>.').format(
            allowed_image_extensions=', '.join(settings.ALLOWED_IMAGE_EXTENSIONS),
            max_size=settings.MAX_IMAGE_UPLOAD_SIZE_MB
        )
    )
    gender = models.CharField(max_length=17, choices=GenderChoices.choices, default=GenderChoices.PREFER_NOT_TO_SAY, blank=True, null=True, verbose_name=_('Gender'))
    birthdate = models.DateField(blank=True, null=True, validators=[BirthdateValidator()], verbose_name=_("Birth Date"))
    national_code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("National Code"))

    class Meta:
        verbose_name = _("profile")
        verbose_name_plural = _("profiles")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('assets/images/placeholders/avatar.webp')


class OTP(TimeStampedModel):
    class TypeChoices(models.TextChoices):
        SMS = 'sms', _('SMS')
        EMAIL = 'email', _('Email')

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', _('Pending')
        VERIFIED = 'verified', _('Verified')
        EXPIRED = 'expired', _('Expired')
        FAILED = 'failed', _('Failed')

    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name='otps', verbose_name=_("User"))
    code = models.CharField(max_length=settings.OTP_SETTINGS.get('OTP_LENGTH', 6), verbose_name=_("OTP Code"))
    otp_type = models.CharField(max_length=10, choices=TypeChoices.choices, verbose_name=_("OTP Type"))
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name=_("Status"))
    recipient = models.CharField(max_length=255, verbose_name=_("Recipient"))
    attempts = models.PositiveIntegerField(default=0, verbose_name=_("Attempt Count"))
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Verified At"))

    objects = OTPManager()

    class Meta:
        verbose_name = _("One-Time Password")
        verbose_name_plural = _("One-Time Passwords")
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'otp_type', 'status']),
            models.Index(fields=['recipient', 'code', 'status']),
        ]

    def __str__(self):
        return f"OTP for {self.recipient} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.pk:
            expiry_minutes = settings.OTP_SETTINGS.get('OTP_EXPIRY_MINUTES', 2)
            self.expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def increment_attempts(self):
        self.attempts += 1
        self.save(update_fields=['attempts'])

    def mark_as_verified(self):
        self.status = self.StatusChoices.VERIFIED
        self.verified_at = timezone.now()
        self.save(update_fields=['status', 'verified_at'])

    def mark_as_failed(self):
        self.status = self.StatusChoices.FAILED
        self.save(update_fields=['status'])


class Address(TimeStampedModel):
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name=_("User"),
        help_text=_("The user this address belongs to.")
    )
    title = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_("Address Title"),
        help_text=_("A short title for the address, e.g., 'Home', 'Office'. (Optional)")
    )
    full_name = models.CharField(
        max_length=255,
        verbose_name=_("Full Name"),
        help_text=_("Full name of the recipient.")
    )
    phone_number = PhoneNumberField(
        verbose_name=_("Phone Number"),
        help_text=_("Phone number of the recipient.")
    )
    country = CountryField(
        blank=False,
        null=False,
        blank_label=_('(select country)'),
        verbose_name=_("Country/Region"),
        help_text=_("The country or region of the address. (Required)")
    )
    city = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name=_("City"),
        help_text=_("The city of the address. (Required)")
    )
    state = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name=_("State/Province"),
        help_text=_("The state or province of the address. (Required)")
    )
    zip_code = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        verbose_name=_("Zip/Postal Code"),
        help_text=_("The zip or postal code of the address. (Required)")
    )
    address_line_1 = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name=_("Address Line 1"),
        help_text=_("Additional address line, e.g., apartment or suite number. (Optional)")
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Address Line 2 (Optional)"),
        help_text=_("e.g., apartment, suite, or unit number.")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Default Address"),
        help_text=_("Set as the default shipping or billing address for the user.")
    )
    is_snapshot = models.BooleanField(
        default=False,
        verbose_name=_("Snapshot Address"),
        help_text=_("Indicates if this address is a snapshot of a previous address.")
    )

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Addresses")
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        user_str = str(self.user) if self.user else "Snapshot"
        return f"Address for {user_str}: {self.city}, {self.address_line_1}"

    def save(self, *args, **kwargs):
        if self.user and self.is_default:
            self.user.addresses.filter(is_snapshot=False, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def get_full_address(self):
        """A property to return the formatted full address."""
        parts = [self.address_line_1, self.address_line_2, self.city, self.state, self.zip_code, self.country.name]
        return ", ".join(part for part in parts if part)


class Wishlist(TimeStampedModel):
    """Represents a user's wishlist, containing specific product variants."""
    user = models.OneToOneField(
        "User",
        on_delete=models.CASCADE,
        related_name='wishlist',
        verbose_name=_("User"),
        help_text=_("The user who owns this wishlist.")
    )
    variants = models.ManyToManyField(
        'products.ProductVariant',
        related_name='wishlisted_by',
        blank=True,
        verbose_name=_("Product Variants"),
        help_text=_("The specific product variants that the user has added to their wishlist.")
    )

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")

    def __str__(self):
        return f"Wishlist of {self.user}"
