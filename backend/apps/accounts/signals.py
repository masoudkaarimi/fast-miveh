import logging

from django.contrib.auth import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import Profile, User, Wishlist
from apps.accounts.utils import update_user_login_data
from apps.orders.models import Cart
from apps.orders.services import CartService
from apps.products.exceptions import OutOfStockError

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_related_objects(sender, instance, created, **kwargs):
    """Signal to automatically create a Profile and a Wishlist whenever a new User is created."""
    if created:
        try:
            Profile.objects.create(user=instance)
            Wishlist.objects.create(user=instance)
        except Exception as e:
            logger.error(f"Failed to create related objects for user {instance.pk}: {e}")


@receiver(user_logged_in)
def update_last_login_info(sender, request, user, **kwargs):
    """Signal to update user's last login timestamp and IP address when they log in."""
    update_user_login_data(user, request)


@receiver(user_logged_in)
def merge_guest_cart_to_user_cart(sender, request, user, **kwargs):
    """Signal handler to merge a guest's shopping cart with their user cart upon login."""
    try:
        session_key = request.session.session_key
        if not session_key:
            return

        guest_cart = Cart.objects.get(session_key=session_key, user__isnull=True)
        user_cart_service = CartService(user=user)
        user_cart = user_cart_service.cart

        print("Guest Cart ID:", guest_cart.id)

        # If the guest cart is not the same as the user's cart, merge them
        if guest_cart.id != user_cart.id:
            for guest_item in guest_cart.items.all():
                try:
                    print("Merging item:", guest_item.variant.id, "Quantity:", guest_item.quantity)
                    user_cart_service.add_item(
                        variant_id=guest_item.variant.id,
                        quantity=guest_item.quantity
                    )
                except OutOfStockError:
                    # If an item is out of stock, log it and continue with the next items.
                    logger.warning(
                        f"Skipped merging out-of-stock item (Variant ID: {guest_item.variant.id}) "
                        f"for user {user.id} from guest cart."
                    )
                except Exception as item_error:
                    logger.error(
                        f"Unexpected error merging item (Variant ID: {guest_item.variant.id}) "
                        f"for user {user.id}: {item_error}"
                    )

            guest_cart.delete()
    except Cart.DoesNotExist:
        # This is normal if the guest had an empty cart.
        pass
    except Exception as e:
        logger.error(f"Critical error merging guest cart for user {user.id}: {e}")

# @receiver(pre_save, sender=Profile)
# def resize_profile_avatar(sender, instance, **kwargs):
#     """Optimized signal to resize an avatar image before it's saved."""
#     from PIL import Image
#
#     # Do nothing if the instance is new or the avatar hasn't been set.
#     if not instance.pk or not instance.avatar:
#         return
#
#     try:
#         # Get the original avatar from the database
#         old_profile = Profile.objects.get(pk=instance.pk)
#         old_avatar = old_profile.avatar
#     except Profile.DoesNotExist:
#         # This is a new instance, so there's no old avatar to compare against.
#         old_avatar = None
#
#     # If the avatar has not changed, do nothing.
#     if instance.avatar == old_avatar:
#         return
#
#     # Avatar has changed, proceed with resizing
#     # Todo: For production environments, it is highly recommended to offload this image processing to a background task queue like Celery to avoid blocking the request-response cycle.
#     try:
#         img = Image.open(instance.avatar)
#
#         # Define the target size
#         max_width = 300
#         max_height = 300
#
#         # Resize only if the image is larger than the target dimensions
#         if img.height > max_height or img.width > max_width:
#             img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
#             # Notice: Overwriting the same file path is done here because we are in `pre_save`. The file object in memory is modified before Django saves it. This is generally safe but requires careful handling.
#             img.save(instance.avatar.path, format=img.format, quality=85)
#
#     except Exception as e:
#         # Log the error but don't block the save operation.
#         logger.error(f"Error resizing avatar for profile {instance.pk}: {e}")
