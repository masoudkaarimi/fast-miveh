import stripe
from django.conf import settings
from django.http import HttpRequest
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order
from apps.payments.exceptions import PaymentInitiationError, PaymentVerificationError
from apps.payments.gateways.base import BasePaymentGateway


class StripeGateway(BasePaymentGateway):
    """Stripe Payment Gateway Integration."""

    def __init__(self, **config: object):
        super().__init__(**config)

        self.api_key = self.config.get('API_KEY')
        if not self.api_key:
            raise ValueError("Stripe API_KEY is not configured.")
        stripe.api_key = self.api_key

    def initiate_payment(self, order: Order, request: HttpRequest):
        # Build the success URL. Stripe will append the session_id to this URL.
        # Example: https://yoursite.com/payments/verify?session_id={CHECKOUT_SESSION_ID}
        success_url = request.build_absolute_uri(reverse('payments:transaction_verify')) + '?session_id={CHECKOUT_SESSION_ID}'
        # You should have a dedicated page in your frontend for cancellation.
        cancel_url = settings.FRONTEND_URL.get("PAYMENT_CANCEL_PAGE", "/")

        # --- IMPORTANT: Currency and Amount ---
        # Stripe requires amounts in the smallest currency unit (e.g., cents for USD).
        # It also requires standard ISO currency codes (e.g., 'usd', 'eur').
        # This example assumes the currency is USD. You'll need a currency conversion
        # mechanism if your base currency is something else like 'TOMAN'.
        currency = 'usd'
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': currency,
                    'product_data': {
                        'name': f"{item.product_title} ({item.variant_title})",
                    },
                    'unit_amount': int(item.unit_price * 100),  # Convert price to cents
                },
                'quantity': item.quantity,
            })

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                # Link the session to our internal order for reference
                client_reference_id=str(order.id)
            )

            # The session ID acts as our gateway_token
            gateway_token = checkout_session.id
            payment_url = checkout_session.url
            return payment_url, gateway_token

        except stripe.error.StripeError as e:
            # Handle specific Stripe API errors
            raise PaymentInitiationError(f"Stripe API error: {e}")
        except Exception as e:
            # Handle other unexpected errors
            raise PaymentInitiationError(f"An unexpected error occurred: {e}")

    def verify_payment(self, request: HttpRequest):
        session_id = request.GET.get('session_id')
        if not session_id:
            raise PaymentVerificationError("Stripe session_id not found in callback.")

        try:
            session = stripe.checkout.Session.retrieve(session_id)

            if session.payment_status == 'paid':
                # The payment was successful. The transaction ID is the Payment Intent ID.
                transaction_id = session.payment_intent
                return True, str(transaction_id), session.to_dict()
            else:
                # The payment was not successful (e.g., requires_action, canceled).
                raise PaymentVerificationError(f"Payment not successful. Status: {session.payment_status}")

        except stripe.error.StripeError as e:
            raise PaymentVerificationError(f"Stripe API error during verification: {e}")
        except Exception as e:
            raise PaymentVerificationError(f"An unexpected error occurred during verification: {e}")

    def parse_token(self, query_params: dict) -> str | None:
        return query_params.get('session_id')
