import logging

from celery import shared_task
from django.conf import settings

from apps.notifications.services import NotificationChannelService, NotificationService

logger = logging.getLogger(__name__)


@shared_task(name="products.send_back_in_stock_notifications")
def send_back_in_stock_notifications(variant_id):
    """Sends notifications to users who subscribed to be notified when a product variant is back in stock."""
    from apps.notifications.models import Notification as NotificationModel
    from apps.products.models import BackInStockSubscription, ProductVariant

    try:
        variant = ProductVariant.objects.select_related('product', 'inventory').get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        logger.warning(f"Variant with id {variant_id} not found for back-in-stock task.")
        return

    if not hasattr(variant, 'inventory') or not variant.inventory.is_in_stock:
        logger.info(f"Stock notification for '{variant.name}' ({variant_id}) skipped as it's no longer in stock.")
        return

    subscriptions = BackInStockSubscription.objects.filter(variant_id=variant_id, status=BackInStockSubscription.StatusChoices.PENDING).select_related('user')
    if not subscriptions.exists():
        return f"No pending subscriptions for variant {variant_id}."

    channel_service = NotificationChannelService()
    notifications_sent_count = 0

    for subscription in subscriptions:
        try:
            if subscription.user:
                in_app_service = NotificationService(recipient=subscription.user)
                in_app_service.create(
                    title="Your favorite product is back in stock!",
                    body=f"The product '{variant.product.name} - {variant.name}' you were waiting for is available again.",
                    category=NotificationModel.Category.ACTIVITIES,
                    related_object=variant
                )

            recipient_email = subscription.user.email if subscription.user else subscription.email
            if recipient_email:
                email_context = {
                    'product_name': variant.product.name,
                    'variant_name': variant.name,
                    'product_url': f"{settings.FRONTEND_URL.get("BASE")}/products/{variant.product.slug}",
                    'site_name': settings.SITE_NAME
                }

                channel_service.send_email(
                    recipient=recipient_email,
                    subject=f"Good news! The product {variant.product.name} is back in stock",
                    template_name='notifications/email/back_in_stock.html',
                    context=email_context
                )

            notifications_sent_count += 1

        except Exception as e:
            logger.error(f"Failed to process subscription {subscription.id} for variant {variant_id}: {e}")

    if notifications_sent_count > 0:
        subscriptions.update(status=BackInStockSubscription.StatusChoices.SENT)

    logger.info(f"Processed {len(subscriptions)} subscription(s) for variant {variant_id}.")
    return f"Processed {len(subscriptions)} subscriptions."
