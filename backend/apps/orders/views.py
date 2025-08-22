from django.db.models import Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.orders.models import Order, CartItem
from apps.orders.serializers import (
    CartItemAddSerializer,
    CartItemUpdateSerializer,
    CartSerializer,
    CheckoutSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderSummarySerializer,
)
from apps.orders.services import CartService, OrderService
from apps.products.exceptions import OutOfStockError


class CartViewSet(viewsets.ViewSet):
    """A viewset for managing the shopping cart."""
    permission_classes = [AllowAny]

    def _get_cart_service(self, request):
        """Helper method to get the appropriate CartService instance."""
        if request.user.is_authenticated:
            return CartService(user=request.user)

        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return CartService(session_key=session_key)

    def list(self, request, *args, **kwargs):  # <-- *args, **kwargs added
        """Retrieve the current user's or guest's cart."""
        cart_service = self._get_cart_service(request)
        cart_data = cart_service.get_data()
        serializer = CartSerializer(cart_data)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):  # <-- *args, **kwargs added
        """Add a new item to the cart."""
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        cart_service = self._get_cart_service(request)
        try:
            cart_service.add_item(variant_id=validated_data['variant_id'], quantity=validated_data['quantity'])
        except OutOfStockError as e:
            raise ValidationError({'detail': str(e)})
        except Exception as e:
            return Response({'detail': 'An unexpected error occurred.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_data = cart_service.get_data()
        output_serializer = CartSerializer(cart_data)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path=r'items/(?P<item_pk>\d+)')
    def update_item(self, request, item_pk=None, *args, **kwargs):
        """Update the quantity of a specific item in the cart."""
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quantity = serializer.validated_data['quantity']

        cart_service = self._get_cart_service(request)
        try:
            cart_service.update_item_quantity(item_id=int(item_pk), quantity=quantity)
        except OutOfStockError as e:
            raise ValidationError({'detail': str(e)})
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in the cart.'}, status=status.HTTP_404_NOT_FOUND)

        cart_data = cart_service.get_data()
        output_serializer = CartSerializer(cart_data)
        return Response(output_serializer.data)

    @action(detail=False, methods=['delete'], url_path=r'items/(?P<item_pk>\d+)')
    def remove_item(self, request, item_pk=None, *args, **kwargs):
        """Remove a specific item from the cart."""
        cart_service = self._get_cart_service(request)
        try:
            cart_service.remove_item(item_id=int(item_pk))
        except CartItem.DoesNotExist:
            return Response({'detail': 'Item not found in the cart.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def clear(self, request, *args, **kwargs):
        """Clear all items from the cart."""
        cart_service = self._get_cart_service(request)
        cart_service.clear()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutAPIView(APIView):
    """Handles the final checkout process."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Process the checkout request to create a new order from the user's cart."""
        serializer = CheckoutSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        user = request.user

        cart_service = CartService(user=user)
        cart = cart_service.cart

        # Get the address objects
        shipping_address = Address.objects.get(pk=validated_data['shipping_address_id'])
        billing_address = None
        if validated_data.get('billing_address_id'):
            billing_address = Address.objects.get(pk=validated_data['billing_address_id'])

        order_service = OrderService(user=user)
        try:
            order = order_service.create_order_from_cart(
                cart=cart,
                shipping_address=shipping_address,
                billing_address=billing_address,
                notes=validated_data.get('notes', '')
            )
        except (ValueError, OutOfStockError) as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        summary_serializer = OrderSummarySerializer(order)
        return Response(summary_serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset for managing orders, allowing users to view their own orders."""
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).annotate(total_items_count=Sum('items__quantity'))

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderDetailSerializer
