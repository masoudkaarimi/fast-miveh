import six
from django.contrib.auth.tokens import PasswordResetTokenGenerator as BasePasswordResetTokenGenerator


class PasswordResetTokenGenerator(BasePasswordResetTokenGenerator):
    """
    Custom token generator for password reset links.
    Invalidates the link once the password is changed or the user becomes inactive.
    """

    def _make_hash_value(self, user, timestamp):
        return (
                six.text_type(user.pk) +
                six.text_type(timestamp) +
                six.text_type(user.is_active) +
                six.text_type(user.password)
        )


password_reset_token_generator = PasswordResetTokenGenerator()
