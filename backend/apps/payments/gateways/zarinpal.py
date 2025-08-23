import logging

from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from zarinpal import ZarinPal
from zarinpal_utils.Config import Config

from apps.orders.models import Order
from apps.payments.exceptions import PaymentInitiationError, PaymentVerificationError
from apps.payments.gateways.base import BasePaymentGateway
from apps.payments.models import PaymentTransaction

logger = logging.getLogger(__name__)


class ZarinpalGateway(BasePaymentGateway):
    """Zarinpal Payment Gateway Integration."""

    def __init__(self, **config: object) -> None:
        super().__init__(**config)

        merchant_id = self.config.get('MERCHANT_ID')
        sandbox = self.config.get('SANDBOX', False)

        if not merchant_id or not isinstance(merchant_id, str):
            raise ValueError("Zarinpal MERCHANT_ID is not configured or is not a string.")

        if not isinstance(sandbox, bool):
            raise ValueError("Zarinpal SANDBOX setting must be a boolean.")

        self.zarinpal = ZarinPal(Config(
            merchant_id=merchant_id,
            sandbox=sandbox
        ))

    def initiate_payment(self, order: Order, request: HttpRequest, callback_url: str = None):
        try:
            frontend_url = settings.FRONTEND_URL.get('PAYMENT_VERIFICATION')
            if not frontend_url:
                raise PaymentInitiationError("Frontend verification URL is not configured in settings.")

            response = self.zarinpal.payments.create({
                "amount": int(order.final_price),
                "callback_url": frontend_url,  # f"{frontend_url}?order_number={order.order_number}",
                "description": _("Payment for Order #{order_number}").format(order_number=order.order_number),
                "mobile": str(order.user.phone_number) if order.user.phone_number else None,
                "email": order.user.email if order.user.email else None,
            })

            if "data" in response and "authority" in response["data"]:
                authority = response["data"]["authority"]
                payment_url = self.zarinpal.payments.generate_payment_url(authority)
                return payment_url, authority

            error_details = response.get('errors', 'Unknown error from Zarinpal')
            logger.error(f"Zarinpal initiation failed for order {order.order_number}. Response: {error_details}")
            raise PaymentInitiationError(error_details)

        except Exception as e:
            logger.error(f"An unexpected error occurred during Zarinpal initiation for order {order.order_number}: {e}", exc_info=True)
            raise PaymentInitiationError(_("An unexpected error occurred while connecting to the payment gateway.")) from e

    def verify_payment(self, query_params: dict):
        authority = query_params.get('authority')
        status = query_params.get('status')

        if not authority or status != 'OK':
            logger.warning(f"Payment verification failed or was canceled. Authority: {authority}, Status: {status}")
            raise PaymentVerificationError(_("Payment was not successful or was canceled by the user."))

        try:
            transaction = PaymentTransaction.objects.get(gateway_token=authority)
            amount_to_verify = int(transaction.amount)
        except PaymentTransaction.DoesNotExist:
            logger.error(f"CRITICAL: No matching transaction found for authority code: {authority}")
            raise PaymentVerificationError(_("Transaction not found."))

        try:
            response = self.zarinpal.verifications.verify({
                "amount": amount_to_verify,
                "authority": authority,
            })

            if response.get("data", {}).get("code") in [100, 101]:
                ref_id = response["data"]["ref_id"]
                logger.info(f"Payment verified successfully for authority {authority}. Ref ID: {ref_id}")
                return True, str(ref_id), response

            error_code = response.get("data", {}).get("code", "N/A")
            error_message = response.get("data", {}).get("message", "Verification failed")
            logger.error(f"Zarinpal verification failed for authority {authority}. Zarinpal error code: {error_code} - Message: {error_message}")
            raise PaymentVerificationError(error_message)

        except Exception as e:
            logger.error(f"An unexpected error occurred during Zarinpal verification for authority {authority}: {e}", exc_info=True)
            raise PaymentVerificationError(_("An unexpected error occurred while verifying the payment.")) from e

    def parse_token(self, query_params):
        return query_params.get('authority')
