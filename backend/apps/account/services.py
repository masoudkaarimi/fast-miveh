from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.account.models import OTP
from apps.account.exceptions import OTPGenerationError, OTPValidationError, OTPCooldownError


class OTPService:
    def __init__(self, user):
        self.user = user

    def _check_cooldown(self, otp_type, recipient):
        """Prevents sending OTPs too frequently and calculates remaining time."""
        cooldown_seconds = settings.OTP_SETTINGS.get('COOLDOWN_SECONDS', 60)
        cooldown_time = timezone.now() - timedelta(seconds=cooldown_seconds)

        latest_otp = OTP.objects.filter(
            user=self.user,
            type=otp_type,
            recipient=recipient,
            created_at__gte=cooldown_time
        ).order_by('-created_at').first()

        if latest_otp:
            cooldown_end_time = latest_otp.created_at + timedelta(seconds=cooldown_seconds)
            remaining_cooldown = cooldown_end_time - timezone.now()
            remaining_seconds = max(0, int(remaining_cooldown.total_seconds()))

            if remaining_seconds > 0:
                raise OTPCooldownError(
                    _("Please wait %(seconds)d seconds before requesting a new code.") % {'seconds': remaining_seconds},
                    remaining_seconds=remaining_seconds
                )

        # if OTP.objects.filter(user=self.user, type=otp_type, recipient=recipient, created_at__gte=cooldown_time).exists():
        #     raise OTPCooldownError(_("Please wait %(seconds)d seconds before requesting a new code.") % {'seconds': cooldown_seconds})

    def generate_and_send_otp(self, otp_type, recipient):
        """Main method to generate, store, and trigger the sending of an OTP."""
        self._check_cooldown(otp_type, recipient)
        otp_instance = OTP.objects.create_otp(self.user, otp_type, recipient)

        try:
            if otp_type == OTP.TypeChoices.EMAIL:
                self.user.email_user(
                    subject=_("Your Verification Code"),
                    message=_("Your verification code is: %(otp_code)s") % {'otp_code': otp_instance.code},
                    template_name='notifications/email/otp.html',
                    context={'otp_code': otp_instance.code, 'site_name': settings.SITE_NAME}
                )
            elif otp_type == OTP.TypeChoices.SMS:
                self.user.sms_user(message=_("Your verification code is: %(otp_code)s") % {'otp_code': otp_instance.code})
        except Exception as e:
            # If sending fails, delete the created OTP to allow immediate retry
            otp_instance.delete()
            raise OTPGenerationError(_("Failed to send OTP. Please try again later."))

        return otp_instance

    def verify_otp(self, otp_type, recipient, code):
        """Validates an OTP code with improved logic for handling different states."""
        max_attempts = settings.OTP_SETTINGS.get('MAX_ATTEMPTS', 5)
        otp_instance = OTP.objects.get_latest_otp(self.user, otp_type, recipient)

        if not otp_instance:
            raise OTPValidationError(_("No OTP found for this recipient. Please request a new one."))

        if otp_instance.status == OTP.StatusChoices.VERIFIED:
            raise OTPValidationError(_("This OTP has already been used and verified."))

        if otp_instance.status in [OTP.StatusChoices.EXPIRED, OTP.StatusChoices.FAILED]:
            raise OTPValidationError(_("This OTP is no longer valid. Please request a new one."))

        if otp_instance.is_expired:
            otp_instance.mark_as_failed()
            raise OTPValidationError(_("OTP code has expired."))

        if otp_instance.attempts >= max_attempts:
            otp_instance.mark_as_failed()
            raise OTPValidationError(_("Maximum verification attempts exceeded."))

        if otp_instance.code != code:
            otp_instance.increment_attempts()
            # After incrementing, check if it now exceeds max attempts
            if otp_instance.attempts >= max_attempts:
                otp_instance.mark_as_failed()
                raise OTPValidationError(_("Invalid OTP code. Maximum attempts exceeded."))
            else:
                # Notice: Revealing remaining attempts may reduce security. Consider removing this message.
                remaining_attempts = max_attempts - otp_instance.attempts
                raise OTPValidationError(_(f"Invalid OTP code. You have {remaining_attempts} attempts remaining."))
                # raise OTPValidationError(_("Invalid OTP code."))

        otp_instance.mark_as_verified()
        return True
