import logging

from celery import shared_task
from django.utils.translation import gettext_lazy as _

from apps.notifications.services import NotificationService
from apps.payments.models import PaymentTransaction

logger = logging.getLogger(__name__)


@shared_task(name="payments.process_successful_payment_notifications")
def process_successful_payment_notifications(transaction_id: str):
    """Task to handle post-payment success actions such as sending notifications and emails."""
    try:
        transaction = PaymentTransaction.objects.select_related('content_object__user').get(id=transaction_id)
        order = transaction.content_object
        user = order.user

        # Send an in-app notification
        notification_service = NotificationService(recipient=user)
        notification_service.create(
            title=_("Payment Successful"),
            body=_("Your payment for order #{order_number} was successful.").format(order_number=order.order_number),
            category="payments",
            related_object=order
        )

        # Send a confirmation email
        user.email_user(
            subject=_("Your Order Confirmation"),
            message=_("Details about your successful order..."),
            # template_name='notifications/email/order_confirmation.html', # TODO: Implement email templates
            # context={'order': order}
        )

        logger.info(f"Successfully processed post-payment notifications for transaction {transaction_id}")
        return f"Notifications sent for transaction {transaction_id}"

    except PaymentTransaction.DoesNotExist:
        logger.error(f"Transaction with ID {transaction_id} not found for post-payment task.")
    except Exception as e:
        logger.error(f"An error occurred in post-payment task for transaction {transaction_id}: {e}", exc_info=True)
        raise
