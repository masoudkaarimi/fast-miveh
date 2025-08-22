from rest_framework import serializers

from apps.accounts.models import Address
from apps.orders.models import Order, OrderItem


class CartItemSerializer(serializers.Serializer):
    """Serializes the details of a single item in the cart. This is a read-only serializer."""
    id = serializers.IntegerField(read_only=True)
    variant_id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    variant_name = serializers.CharField(read_only=True)
    sku = serializers.CharField(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    image_url = serializers.URLField(read_only=True, allow_null=True)


class CartSerializer(serializers.Serializer):
    """Serializes the entire cart object, including a list of its items. This is a read-only serializer."""
    id = serializers.UUIDField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    items = CartItemSerializer(many=True, read_only=True)


class CartItemAddSerializer(serializers.Serializer):
    """Serializes the input data for adding a new item to the cart."""
    variant_id = serializers.IntegerField(write_only=True, required=True)
    quantity = serializers.IntegerField(write_only=True, default=1, min_value=1)


class CartItemUpdateSerializer(serializers.Serializer):
    """Serializes the input data for updating an existing item in the cart."""
    quantity = serializers.IntegerField(write_only=True, required=True, min_value=0)


class CheckoutSerializer(serializers.Serializer):
    """Serializes the input data required to create a new order during checkout."""
    shipping_address_id = serializers.IntegerField(required=True)
    billing_address_id = serializers.IntegerField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_shipping_address_id(self, value):
        """Check that the shipping address exists and belongs to the current user."""
        user = self.context['request'].user
        if not Address.objects.filter(pk=value, user=user, is_snapshot=False).exists():
            raise serializers.ValidationError("Shipping address not found or does not belong to the user.")
        return value

    def validate_billing_address_id(self, value):
        """Check that the billing address (if provided) exists and belongs to the current user."""
        if value is None:
            return None
        user = self.context['request'].user
        if not Address.objects.filter(pk=value, user=user, is_snapshot=False).exists():
            raise serializers.ValidationError("Billing address not found or does not belong to the user.")
        return value


class OrderSummarySerializer(serializers.Serializer):
    """Provides a summary of the created order upon successful checkout."""
    order_number = serializers.CharField(read_only=True)
    final_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)


class OrderAddressSerializer(serializers.ModelSerializer):
    """Serializes the address details for an order, including full name and phone number."""
    address = serializers.CharField(source='get_full_address', read_only=True)

    class Meta:
        model = Address
        fields = ('title', 'full_name', 'phone_number', 'address')


class OrderItemDetailSerializer(serializers.ModelSerializer):
    """Serializes the details of a single item within an order."""

    class Meta:
        model = OrderItem
        fields = ('product_title', 'variant_title', 'sku', 'unit_price', 'quantity', 'total_price', 'attributes_snapshot',)


class OrderListSerializer(serializers.ModelSerializer):
    """Serializes a summary of each order for the list view."""
    total_items = serializers.IntegerField(source='total_items_count', read_only=True)

    class Meta:
        model = Order
        fields = ('order_number', 'status', 'final_price', 'total_items', 'created_at',)


class OrderDetailSerializer(serializers.ModelSerializer):
    """Serializes the detailed information of a single order."""
    items = OrderItemDetailSerializer(many=True, read_only=True)
    shipping_address = OrderAddressSerializer(read_only=True)
    billing_address = OrderAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'order_number', 'status', 'created_at', 'subtotal_price', 'shipping_price', 'discount_amount',
            'final_price', 'notes', 'shipping_address', 'billing_address', 'items',
        )
