from django.templatetags.static import static
from rest_framework import serializers

from apps.core.models import SiteConfiguration
from apps.orders.models import Order
from apps.payments.models import PaymentGateway, PaymentTransaction
from apps.wallets.models import Wallet


class PaymentGatewaySerializer(serializers.ModelSerializer):
    """Serializes the payment gateway details."""
    is_default = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    supported_countries = serializers.ListField(child=serializers.CharField(), source='get_supported_countries_list', read_only=True)

    class Meta:
        model = PaymentGateway
        fields = ('identifier', 'name', 'logo_url', 'description', 'min_amount', 'supported_countries', 'is_default')

    def get_is_default(self, obj):
        # Gets the site config and checks if this gateway is the default one
        config = SiteConfiguration.get_solo()
        if config.default_payment_gateway:
            return obj.pk == config.default_payment_gateway.pk
        return False

    def get_logo_url(self, obj):
        """Generates the absolute URL for the brand logo."""
        request = self.context.get('request')

        if obj.logo and hasattr(obj.logo, 'url'):
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url

        placeholder_url = static('assets/images/placeholders/payment_gateway_logo_placeholder.webp')
        return request.build_absolute_uri(placeholder_url) if request else placeholder_url


class PaymentTransactionListSerializer(serializers.ModelSerializer):
    """Serializes the list view of payment transactions."""
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    related_object_description = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTransaction
        fields = ('id', 'amount', 'currency', 'status_display', 'gateway_name', 'related_object_description', 'created_at',)

    def get_related_object_description(self, obj):
        """Returns a user-friendly description of what the transaction was for."""
        content_object = obj.content_object
        if isinstance(content_object, Order):
            return f"Order #{content_object.order_number}"
        if isinstance(content_object, Wallet):
            return "Wallet Charge"
        return "General Transaction"


class PaymentTransactionDetailSerializer(serializers.ModelSerializer):
    """Serializes the detailed view of a payment transaction."""
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    related_object_description = serializers.SerializerMethodField()

    class Meta:
        model = PaymentTransaction
        fields = ('id', 'amount', 'currency', 'status_display', 'gateway_name', 'gateway_transaction_id', 'related_object_description', 'created_at',)

    def get_related_object_description(self, obj):
        """Returns a user-friendly description of what the transaction was for."""
        content_object = obj.content_object
        if isinstance(content_object, Order):
            return f"Order #{content_object.order_number}"
        if isinstance(content_object, Wallet):
            return "Wallet Charge"
        return "General Transaction"


class PaymentURLSerializer(serializers.Serializer):
    """Serializes the response containing the payment URL."""
    payment_url = serializers.URLField(read_only=True)
    gateway_token = serializers.CharField(read_only=True)


class PaymentTransactionCreateSerializer(serializers.Serializer):
    """Serializes the input for creating a payment transaction."""
    order_number = serializers.CharField(write_only=True, required=True)
    gateway_identifier = serializers.SlugField(write_only=True, required=True)

    def validate_order_number(self, value):
        """Validates that the order exists, belongs to the user, and is pending payment."""
        user = self.context['request'].user
        try:
            order = Order.objects.get(order_number=value, user=user, status=Order.OrderStatusChoices.PENDING_PAYMENT)
            self.context['order'] = order
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found, does not belong to you, or is not pending payment.")


class PaymentTransactionVerifySerializer(serializers.Serializer):
    """Serializes the input for verifying a payment transaction."""
    gateway_identifier = serializers.SlugField(write_only=True, required=True)
    callback_params = serializers.DictField(write_only=True, required=True, child=serializers.CharField(allow_blank=True))


class PaymentVerificationResultSerializer(serializers.Serializer):
    """Serializes the result of a payment verification attempt."""
    order_number = serializers.CharField(read_only=True, required=False)
    status = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)
