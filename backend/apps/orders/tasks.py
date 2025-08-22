import datetime
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="orders.cleanup_abandoned_carts")
def cleanup_abandoned_carts(days_old=30):
    """
    Deletes old, abandoned guest carts from the database.

    An abandoned cart is one that is not associated with a user (guest cart)
    and hasn't been updated for a specified number of days.
    """
    from apps.orders.models import Cart

    try:
        cutoff_date = timezone.now() - datetime.timedelta(days=days_old)

        logger.info(f"Starting task to clean up abandoned carts older than {days_old} days (before {cutoff_date.strftime('%Y-%m-%d')}).")

        abandoned_carts = Cart.objects.filter(user__isnull=True, updated_at__lt=cutoff_date)

        cart_count = abandoned_carts.count()
        if cart_count > 0:
            result = abandoned_carts.delete()
            logger.info(f"Successfully deleted {cart_count} abandoned cart(s). Full result: {result}")
            return f"Successfully deleted {cart_count} abandoned cart(s)."
        else:
            logger.info("No abandoned carts found to delete.")
            return "No abandoned carts found to delete."

    except Exception as e:
        logger.error(f"An error occurred during abandoned cart cleanup: {e}", exc_info=True)
        raise
