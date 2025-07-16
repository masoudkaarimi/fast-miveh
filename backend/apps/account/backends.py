import logging
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logger = logging.getLogger(__name__)

User = get_user_model()


class IdentifierBackend(ModelBackend):
    """A custom authentication backend that allows users to log in using either their verified email address or their phone number."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticates a user based on a provided identifier (email or phone) and password."""
        if username is None:
            return None

        # Create a query to find the user by either phone number or a verified email.
        user_query = User.objects.filter(Q(phone_number=username) | Q(email__iexact=username, is_email_verified=True))

        try:
            user = user_query.get()

            # Check the password and if the user is permitted to authenticate.
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            else:
                logger.warning(f"Authentication failed for identifier '{username}': invalid credentials or inactive user.")

        except User.DoesNotExist:
            logger.warning(f"Authentication failed: no user found for identifier '{username}'.")
            # To prevent user enumeration attacks through timing analysis, we run the password hashing function on a dummy user object. This ensures the response time is nearly identical whether the user exists or not.
            User().set_password(password)

        except User.MultipleObjectsReturned:
            logger.error(f"Authentication failed: multiple users found for identifier '{username}'. This indicates a data integrity issue.")

        return None

    def get_user(self, user_id):
        """Retrieves a user instance from the database, given a user ID. This is required for the session framework to work correctly."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f"Failed to get user with id={user_id}: User does not exist.")
            return None


class OTPBackend(ModelBackend):
    """Authenticates a user based on a pre-validated user object, typically after a successful OTP verification. This backend does not check a password."""

    def authenticate(self, request, user=None, **kwargs):
        """Authenticates a pre-validated user object."""
        if user and self.user_can_authenticate(user):
            return user

        if user:
            logger.warning(f"OTP authentication failed for inactive user: {user}")

        return None

    def get_user(self, user_id):
        """Retrieves a user instance from the database, given a user ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.warning(f"Failed to get user with id={user_id}: User does not exist.")
            return None
