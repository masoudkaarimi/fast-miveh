import logging

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext as _
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.payments.exceptions import PaymentGatewayError, PaymentVerificationError
from apps.payments.models import PaymentGateway, PaymentTransaction
from apps.payments.serializers import (
    PaymentGatewaySerializer,
    PaymentTransactionCreateSerializer,
    PaymentTransactionDetailSerializer,
    PaymentTransactionListSerializer,
    PaymentTransactionVerifySerializer,
    PaymentURLSerializer,
    PaymentVerificationResultSerializer,
)
from apps.payments.services import TransactionService
from apps.wallets.exceptions import InsufficientFundsError
from apps.wallets.models import Wallet
from apps.wallets.services import WalletService

logger = logging.getLogger(__name__)


class PaymentGatewayListView(generics.ListAPIView):
    """API view to list all active payment gateways."""
    permission_classes = [AllowAny]
    serializer_class = PaymentGatewaySerializer
    pagination_class = None
    filterset_fields = ['identifier', 'name']

    def get_queryset(self):
        queryset = PaymentGateway.objects.filter(is_active=True)

        # Filter by country if provided in query params
        country_code = self.request.query_params.get('country_code')
        if country_code:
            queryset = queryset.filter(Q(supported_countries__icontains=country_code) | Q(supported_countries=''))
        return queryset


class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """API viewset to list and retrieve payment transactions for the authenticated user."""
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return PaymentTransaction.objects.none()

        order_content_type = ContentType.objects.get_for_model(Order)
        wallet_content_type = ContentType.objects.get_for_model(Wallet)

        # Get primary keys of all orders belonging to the user
        user_order_pks_qs = Order.objects.filter(user=user).values_list('pk', flat=True)

        # Explicitly convert the list of UUIDs to a list of strings
        user_order_pks_as_strings = [str(pk) for pk in user_order_pks_qs]

        # Transactions related to the user's orders (now comparing strings with strings)
        order_query = Q(content_type=order_content_type, object_id__in=user_order_pks_as_strings)

        # Transactions related to the user's wallet (its pk is the user's pk)
        wallet_query = Q(content_type=wallet_content_type, object_id=str(user.pk))

        # Combine queries and prefetch the generic content_object for performance
        return PaymentTransaction.objects.filter(order_query | wallet_query).prefetch_related('content_object')

    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentTransactionListSerializer
        return PaymentTransactionDetailSerializer


class PaymentTransactionCreateView(APIView):
    """API view to create (initiate) a payment for a specific order."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        gateway_identifier = serializer.validated_data['gateway_identifier']
        order = serializer.context['order']
        user = request.user

        try:
            # --- Wallet Payment Logic ---
            if gateway_identifier == 'wallet':
                wallet_service = WalletService(user=user)

                description = _("Payment for Order #%(order_number)s") % {'order_number': order.order_number}
                wallet_service.spend(amount=order.final_price, source_object=order, description=description)

                order.status = Order.OrderStatusChoices.PROCESSING
                order.save(update_fields=['status'])

                # TODO: Dispatch notification task for successful wallet payments, similar to gateway payments.

                return Response({"detail": _("Payment successful with wallet.")}, status=status.HTTP_200_OK)

            # --- External Gateway Logic ---
            payment_url, token = TransactionService.initiate_order_payment(order, gateway_identifier, request)
            response_serializer = PaymentURLSerializer({'payment_url': payment_url, 'gateway_token': token})
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except (PaymentGatewayError, InsufficientFundsError) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.error("Unexpected error during payment initiation", exc_info=True)
            return Response({"detail": _("An unexpected server error occurred.")}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentTransactionVerifyView(APIView):
    """API view to verify a payment transaction."""
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentTransactionVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        gateway_identifier = serializer.validated_data['gateway_identifier']
        query_params = serializer.validated_data['callback_params']

        try:
            result = TransactionService.verify_payment(gateway_identifier, query_params)
            response_serializer = PaymentVerificationResultSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except PaymentVerificationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            logger.error("Unexpected error during payment verification", exc_info=True)
            return Response({"detail": "An unexpected server error occurred during verification."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
