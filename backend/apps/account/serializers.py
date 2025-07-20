import logging

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.encoding import smart_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import authenticate, get_user_model, password_validation

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.serializerfields import PhoneNumberField

from apps.common.utils import get_client_ip
from apps.account.models import OTP, Profile
from apps.account.services import OTPService
from apps.account.utils import get_identifier_info
from apps.account.tokens import password_reset_token_generator
from apps.account.exceptions import OTPValidationError, OTPGenerationError, OTPCooldownError

logger = logging.getLogger(__name__)

User = get_user_model()


class IdentifierStatusCheckSerializer(serializers.Serializer):
    """Checks the status of a user based on an identifier (phone number or email)."""
    identifier = serializers.CharField(required=True, write_only=True)
    user_exists = serializers.BooleanField(read_only=True)
    has_password = serializers.BooleanField(read_only=True)

    def validate(self, data):
        identifier = data.get('identifier')

        identifier_type, normalized_identifier = get_identifier_info(identifier)

        user = None
        if identifier_type == 'email':
            user = User.objects.filter(email__iexact=normalized_identifier).first()
        elif identifier_type == 'phone_number':
            user = User.objects.filter(phone_number=normalized_identifier).first()

        return {
            'user_exists': bool(user),
            'has_password': user.has_usable_password() if user else False
        }


class RequestOTPSerializer(serializers.Serializer):
    """Requests an OTP for a phone number. Creates an inactive user if not exists."""
    phone_number = PhoneNumberField(required=True)
    otp_lifetime_seconds = serializers.IntegerField(read_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        user, created = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={
                'username': str(phone_number),
                'is_active': False
            }
        )
        if created:
            user.set_unusable_password()
            user.save()
        self.context['user'] = user
        return data

    def save(self):
        user = self.context['user']
        phone_number = self.validated_data['phone_number']
        otp_service = OTPService(user=user)
        try:
            otp_service.generate_and_send_otp(otp_type=OTP.TypeChoices.SMS, recipient=str(phone_number))
            otp_lifetime = settings.OTP_SETTINGS.get('OTP_EXPIRY_MINUTES', 2) * 60
            self.validated_data['otp_lifetime_seconds'] = otp_lifetime
        except OTPCooldownError as e:
            raise serializers.ValidationError({
                "detail": str(e),
                "cooldown_remaining_seconds": e.remaining_seconds
            })
        except OTPGenerationError as e:
            raise serializers.ValidationError(str(e))
        return user


class VerifyOTPAndLoginSerializer(serializers.Serializer):
    """Verifies an OTP, activates the user if new, and returns JWT tokens."""
    phone_number = PhoneNumberField(required=True, write_only=True)
    code = serializers.CharField(required=True, write_only=True, max_length=settings.OTP_SETTINGS.get('OTP_LENGTH', 6))
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    is_new_user = serializers.BooleanField(read_only=True)

    def validate(self, data):
        phone_number = data.get('phone_number')
        code = data.get('code')
        user = User.objects.filter(phone_number=phone_number).first()

        if not user:
            raise serializers.ValidationError(_("Invalid phone number."))

        is_new_user = not user.is_phone_number_verified

        otp_service = OTPService(user=user)
        try:
            if not otp_service.verify_otp(otp_type=OTP.TypeChoices.SMS, recipient=str(phone_number), code=code):
                raise serializers.ValidationError(_("Invalid OTP code."))
        except OTPValidationError as e:
            raise serializers.ValidationError(str(e))

        if not user.is_active or not user.is_phone_number_verified:
            user.is_active = True
            user.is_phone_number_verified = True
            user.save(update_fields=['is_active', 'is_phone_number_verified'])

        authenticated_user = authenticate(request=self.context.get('request'), user=user)

        if not authenticated_user:
            raise serializers.ValidationError(_("Authentication failed after OTP verification. Please contact support."))

        refresh_token = RefreshToken.for_user(authenticated_user)
        return {
            'is_new_user': is_new_user,
            'access_token': str(refresh_token.access_token),
            'refresh_token': str(refresh_token),
            # 'phone_number': str(phone_number),
            # 'code': code
        }


class LoginWithPasswordSerializer(serializers.Serializer):
    """Serializer for user login with an identifier (phone_number or email) and password."""
    identifier = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        identifier_type, normalized_identifier = get_identifier_info(identifier)

        user = None
        try:
            if identifier_type == 'email':
                user = User.objects.get(email__iexact=normalized_identifier)
            elif identifier_type == 'phone_number':
                user = User.objects.get(phone_number=normalized_identifier)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Unable to log in with provided credentials."))

        if not user:
            raise serializers.ValidationError(_("Unable to log in with provided credentials."))

        if not user.check_password(password):
            raise serializers.ValidationError(_("Unable to log in with provided credentials."))

        if not user.is_active:
            raise serializers.ValidationError(_("User account is disabled."))

        if identifier_type == 'email' and not user.is_email_verified:
            raise serializers.ValidationError(_("The email address is not verified. Please log in with your phone number or verify your email."))

        user.last_login_at = timezone.now()
        user.last_login_ip = get_client_ip(request=self.context.get('request'))
        user.save(update_fields=['last_login_at', 'last_login_ip'])

        refresh_token = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh_token.access_token),
            'refresh_token': str(refresh_token),
            # 'identifier': identifier
        }


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the Profile model, used as a nested serializer."""

    class Meta:
        model = Profile
        fields = ('gender', 'birthdate', 'national_code', 'avatar')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for viewing and updating user profile information."""
    profile = ProfileSerializer()
    has_password = serializers.SerializerMethodField()
    is_profile_complete = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'phone_number', 'is_phone_number_verified', 'email', 'is_email_verified',
            'username', 'first_name', 'last_name', 'profile',
            'has_password',
            'is_profile_complete'
        )
        read_only_fields = ('phone_number', 'is_phone_number_verified', 'email', 'is_email_verified', 'has_password', 'is_profile_complete')

    @staticmethod
    def get_has_password(obj):
        return obj.has_usable_password()

    @staticmethod
    def get_is_profile_complete(obj):
        # Todo
        # We consider the profile complete if the user has a first name.
        # You can make this logic more complex if needed.
        return bool(obj.first_name)

    def update(self, instance, validated_data):
        """
        Handles nested updates for the User and its related Profile.
        It will create a profile if one does not exist for the user.
        """
        profile, created = Profile.objects.get_or_create(user=instance)
        profile_data = validated_data.pop('profile', {})

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return super().update(instance, validated_data)


class PasswordSetSerializer(serializers.Serializer):
    """ Serializer for a user to set their password. On success, it returns the full user profile."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, min_length=8)
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Confirm Password")
    user_profile = UserProfileSerializer(read_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if user.has_usable_password():
            raise serializers.ValidationError(_("You already have a password set. Please use the 'change password' feature."))

        password = attrs.get('password')
        password2 = attrs.get('password2')

        if password != password2:
            raise serializers.ValidationError({"password2": _("Password fields didn't match.")})

        try:
            # Use Django's built-in password validation
            password_validation.validate_password(password, user)
        except DjangoValidationError as e:
            # Raise DRF's validation error with the messages from Django
            raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['password'])
        user.save(update_fields=['password'])
        self.validated_data['user_profile'] = user
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for an existing user to change their password."""
    old_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    new_password1 = serializers.CharField(write_only=True, required=True, min_length=8, style={'input_type': 'password'}, label="New Password")
    new_password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="Confirm New Password")

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Your old password was entered incorrectly. Please enter it again."))
        return value

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": _("New password fields didn't match.")})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password1'])
        user.save(update_fields=['password'])
        return user


class EmailAddSerializer(serializers.Serializer):
    """Serializer to add or change a user's email address and send OTP."""
    email = serializers.EmailField(required=True)
    otp_lifetime_seconds = serializers.IntegerField(read_only=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=self.context['request'].user.pk).exists():
            raise serializers.ValidationError(_("This email address is already in use."))
        return value

    def save(self):
        user = self.context['request'].user
        user.email = self.validated_data['email']
        user.is_email_verified = False
        user.save(update_fields=['email', 'is_email_verified'])

        otp_service = OTPService(user=user)
        try:
            otp_service.generate_and_send_otp(otp_type=OTP.TypeChoices.EMAIL, recipient=user.email)

            otp_lifetime = settings.OTP_SETTINGS.get('OTP_EXPIRY_MINUTES', 2) * 60
            self.validated_data['otp_lifetime_seconds'] = otp_lifetime
        except OTPCooldownError as e:
            raise serializers.ValidationError({
                "detail": str(e),
                "cooldown_remaining_seconds": e.remaining_seconds
            })
        except OTPGenerationError as e:
            raise serializers.ValidationError(str(e))
        return user


class EmailVerifySerializer(serializers.Serializer):
    """Serializer to verify an email address using an OTP."""
    code = serializers.CharField(required=True, max_length=settings.OTP_SETTINGS.get('OTP_LENGTH', 6))

    def validate(self, data):
        user = self.context['request'].user
        if not user.email:
            raise serializers.ValidationError(_("No email address has been set for this account."))
        otp_service = OTPService(user=user)
        try:
            if not otp_service.verify_otp(otp_type=OTP.TypeChoices.EMAIL, recipient=user.email, code=data.get('code')):
                raise serializers.ValidationError(_("Invalid OTP code."))
        except OTPValidationError as e:
            raise serializers.ValidationError(str(e))
        return data

    def save(self):
        user = self.context['request'].user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Handles a password reset request for a given identifier (email or phone number).
    If the identifier is a verified email, it sends a password reset link.
    If it's a verified phone number, it sends an OTP code via SMS.
    """
    identifier = serializers.CharField(required=True)

    def validate(self, data):
        """Validates the identifier and finds the corresponding verified user."""
        identifier = data.get('identifier')
        user = None

        identifier_type, normalized_identifier = get_identifier_info(identifier)

        try:
            if identifier_type == 'email':
                user = User.objects.get(email__iexact=normalized_identifier, is_email_verified=True)
            elif identifier_type == 'phone_number':
                user = User.objects.get(phone_number=normalized_identifier, is_phone_number_verified=True)
        except User.DoesNotExist:
            # To prevent user enumeration attacks, we fail silently if the user is not found
            # or their identifier is not verified. The view will return a generic success message.
            pass

        self.context['user'] = user
        self.context['identifier_type'] = identifier_type
        return data

    def save(self, **kwargs):
        """Sends the appropriate password reset instruction (email link or SMS OTP)."""
        user = self.context.get('user')
        identifier_type = self.context.get('identifier_type')

        # If no valid user was found during validation, do nothing.
        if not user or not identifier_type:
            return

        if identifier_type == 'email':
            self._send_password_reset_email(user)
        elif identifier_type == 'phone_number':
            self._send_password_reset_otp(user)

    @staticmethod
    def _send_password_reset_email(user):
        """Generates and sends a password reset email to the user."""
        uid = urlsafe_base64_encode(smart_bytes(user.pk))
        token = password_reset_token_generator.make_token(user)

        # IMPORTANT: This URL should point to your frontend password reset confirmation page.
        frontend_url = settings.FRONTEND_URL.get('PASSWORD_RESET_CONFIRM')
        reset_url = f"{frontend_url}?uidb64={uid}&token={token}"

        user.email_user(
            subject=_("Password Reset Request"),
            message=_("You have requested a password reset. Click the link below to reset your password:\n\n %(reset_url)s") % {'reset_url': reset_url},
            template_name='notifications/email/password_reset.html',
            context={
                'user': user,
                'reset_url': reset_url,
                'site_name': settings.SITE_NAME
            }
        )

    @staticmethod
    def _send_password_reset_otp(user):
        """Generates and sends a password reset OTP to the user's phone."""
        otp_service = OTPService(user=user)
        try:
            otp_service.generate_and_send_otp(otp_type=OTP.TypeChoices.SMS, recipient=str(user.phone_number))
        except (OTPGenerationError, OTPCooldownError) as e:
            # Log the error for debugging, but don't expose it to the client.
            # logger.error(f"Failed to send password reset OTP to {user}: {e}")
            pass


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Handles the actual password reset using a token."""
    uidb64 = serializers.CharField(write_only=True, required=True)
    token = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, attrs):
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uidb64']))
            user = User.objects.get(pk=uid)
            if not password_reset_token_generator.check_token(user, attrs['token']):
                raise serializers.ValidationError(_("The reset link is invalid or has expired."), code='authorization')
            self.context['user'] = user
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError(_("The reset link is invalid or has expired."), code='authorization')
        return attrs

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['password'])
        user.save(update_fields=['password'])
        return user


class PasswordResetConfirmWithOTPSerializer(serializers.Serializer):
    """Handles the actual password reset using an OTP code."""
    phone_number = PhoneNumberField(required=True)
    code = serializers.CharField(required=True, max_length=settings.OTP_SETTINGS.get('OTP_LENGTH', 6))
    password = serializers.CharField(write_only=True, required=True, min_length=8)

    def validate(self, attrs):
        phone_number = attrs['phone_number']
        code = attrs['code']

        try:
            # The condition "is_phone_number_verified=True" is removed from here
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Invalid phone number or user not found."))

        # ... the rest of the validation logic remains the same ...
        otp_service = OTPService(user=user)
        try:
            if not otp_service.verify_otp(otp_type=OTP.TypeChoices.SMS, recipient=str(phone_number), code=code):
                raise serializers.ValidationError(_("Invalid OTP code."))
        except OTPValidationError as e:
            raise serializers.ValidationError(str(e))

        self.context['user'] = user
        return attrs

    def save(self):
        user = self.context['user']
        user.set_password(self.validated_data['password'])
        user.save(update_fields=['password'])
        return user
