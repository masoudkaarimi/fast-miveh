import logging
from PIL import Image
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save, pre_save

from apps.common.utils import get_client_ip
from apps.account.models import Profile, User

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """A signal to automatically create a Profile instance whenever a new User is created."""
    try:
        if created:
            Profile.objects.create(user=instance)
    except Exception as e:
        logger.error(f"Failed to create profile for user {instance.pk}: {e}")


@receiver(user_logged_in)
def update_last_login_info(sender, request, user, **kwargs):
    """Updates the user's last login timestamp and IP address upon login."""
    try:
        user.last_login_ip = get_client_ip(request)
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_ip', 'last_login_at'])
    except Exception as e:
        logger.error(f"Failed to update last login info for user {user.pk}: {e}")


@receiver(pre_save, sender=Profile)
def resize_profile_avatar(sender, instance, **kwargs):
    """Optimized signal to resize an avatar image before it's saved."""

    # Do nothing if the instance is new or the avatar hasn't been set.
    if not instance.pk or not instance.avatar:
        return

    try:
        # Get the original avatar from the database
        old_profile = Profile.objects.get(pk=instance.pk)
        old_avatar = old_profile.avatar
    except Profile.DoesNotExist:
        # This is a new instance, so there's no old avatar to compare against.
        old_avatar = None

    # If the avatar has not changed, do nothing.
    if instance.avatar == old_avatar:
        return

    # Avatar has changed, proceed with resizing
    # Todo: For production environments, it is highly recommended to offload this image processing to a background task queue like Celery to avoid blocking the request-response cycle.
    try:
        img = Image.open(instance.avatar)

        # Define the target size
        max_width = 300
        max_height = 300

        # Resize only if the image is larger than the target dimensions
        if img.height > max_height or img.width > max_width:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            # Notice: Overwriting the same file path is done here because we are in `pre_save`. The file object in memory is modified before Django saves it. This is generally safe but requires careful handling.
            img.save(instance.avatar.path, format=img.format, quality=85)

    except Exception as e:
        # Log the error but don't block the save operation.
        logger.error(f"Error resizing avatar for profile {instance.pk}: {e}")
