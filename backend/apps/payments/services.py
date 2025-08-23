from django.conf import settings
from django.db import transaction
from django.http import HttpRequest
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from apps.core.models import SiteConfiguration
from apps.orders.models import Order
from apps.payments.exceptions import PaymentGatewayError, PaymentGatewayNotFoundError, PaymentVerificationError
from apps.payments.gateways.base import BasePaymentGateway
from apps.payments.models import PaymentGateway, PaymentTransaction
from apps.payments.tasks import process_successful_payment_notifications
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService

# A simple in-memory cache for gateway instances
_gateway_cache = {}


class PaymentGatewayService:
    """Service class for managing payment gateways."""

    @staticmethod
    def get_gateway(identifier: str) -> BasePaymentGateway:
        """
        Finds a gateway by its identifier, loads its class, and initializes it.
        uses a cache to avoid redundant database queries and imports.

        Raises:
            PaymentGatewayNotFoundError: If the gateway is not found, inactive, or misconfigured.
        """
        if identifier in _gateway_cache:
            return _gateway_cache[identifier]

        try:
            PaymentGateway.objects.get(identifier=identifier, is_active=True)

            provider_settings = settings.PAYMENTS_SETTINGS['PROVIDERS'].get(identifier)
            if not provider_settings:
                raise PaymentGatewayNotFoundError(f"No settings found for provider '{identifier}'.")

            gateway_class_path = provider_settings['CLASS_PATH']
            GatewayClass = import_string(gateway_class_path)

            config = provider_settings.get('CONFIG', {})
            instance = GatewayClass(**config)

            _gateway_cache[identifier] = instance
            return instance

        except PaymentGateway.DoesNotExist:
            raise PaymentGatewayNotFoundError(f"Gateway with identifier '{identifier}' not found or is not active.")
        except (KeyError, AttributeError, ImportError) as e:
            raise PaymentGatewayNotFoundError(f"Payment gateway '{identifier}' is misconfigured. Error: {e}") from e


class TransactionService:
    """Service class for handling payment transactions."""

    @staticmethod
    def _get_currency():
        """Gets the default currency from site configuration."""
        return SiteConfiguration.get_solo().default_currency.code

    @classmethod
    def initiate_order_payment(cls, order: Order, gateway_identifier: str, request: HttpRequest):
        """Initiates a payment for the given order using the specified gateway."""
        gateway_service = PaymentGatewayService.get_gateway(identifier=gateway_identifier)

        try:
            payment_url, gateway_token = gateway_service.initiate_payment(order, request)
        except Exception as e:
            raise PaymentGatewayError(f"Gateway connection error: {e}") from e

        PaymentTransaction.objects.create(
            content_object=order,
            gateway=PaymentGateway.objects.get(identifier=gateway_identifier),
            amount=order.final_price,
            currency=cls._get_currency(),
            status=PaymentTransaction.TransactionStatus.PENDING,
            gateway_token=gateway_token
        )

        return payment_url, gateway_token

    @classmethod
    @transaction.atomic
    def verify_payment(cls, gateway_identifier: str, query_params: dict):
        """Verifies the payment with the gateway the transaction if successful."""
        gateway_service = PaymentGatewayService.get_gateway(identifier=gateway_identifier)
        token = gateway_service.parse_token(query_params)

        try:
            transaction_to_verify = PaymentTransaction.objects.select_for_update().get(gateway_token=token)
        except PaymentTransaction.DoesNotExist:
            raise PaymentVerificationError(_("Transaction not found."))

        is_successful, transaction_id, gateway_response = gateway_service.verify_payment(query_params)
        transaction_to_verify.gateway_response = gateway_response

        if is_successful:
            transaction_to_verify.status = PaymentTransaction.TransactionStatus.SUCCESSFUL
            transaction_to_verify.gateway_transaction_id = transaction_id
            transaction_to_verify.save()

            # Fulfill the transaction (update order, dispatch tasks, etc.)
            message = cls._successful_transaction(transaction_to_verify)
            return {"status": "successful", "message": message, "order_number": transaction_to_verify.content_object.order_number}
        else:
            transaction_to_verify.status = PaymentTransaction.TransactionStatus.FAILED
            transaction_to_verify.save()
            raise PaymentVerificationError(_("Payment failed or was cancelled by the gateway."))

    @staticmethod
    def _successful_transaction(transaction: PaymentTransaction) -> str:
        """Handles post-payment success logic."""
        content_object = transaction.content_object
        message = ""

        if isinstance(content_object, Order):
            order = content_object
            order.status = Order.OrderStatusChoices.PROCESSING
            order.save(update_fields=['status'])
            message = _("Order payment was successful.")

            # Dispatch Celery task for notifications
            process_successful_payment_notifications.delay(transaction.id)

        elif isinstance(content_object, Wallet):
            wallet_service = WalletService(user=content_object.user)
            wallet_service.deposit(
                amount=transaction.amount,
                source_object=transaction,
                description=f"Wallet charge via {transaction.gateway.name}"
            )
            message = _("Wallet charged successfully.")
            # You can dispatch a different Celery task for wallet notifications here if needed

        return message
