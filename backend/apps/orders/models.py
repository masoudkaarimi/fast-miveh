import uuid

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel

User = get_user_model()


class Cart(TimeStampedModel):
    """Represents a shopping cart, which can be associated with a user or a session."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        null=True,
        blank=True,
        verbose_name=_("User"),
        help_text=_("The user who owns this cart. Can be null for guest carts.")
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_("Session Key"),
        help_text=_("The session key for guest carts. Can be null if the cart is associated with a user.")
    )

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Carts")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(user__isnull=False),
                name='unique_active_cart_per_user'
            ),
            models.UniqueConstraint(
                fields=['session_key'],
                condition=Q(session_key__isnull=False),
                name='unique_active_cart_per_session'
            ),
            models.CheckConstraint(
                check=Q(user__isnull=False) | Q(session_key__isnull=False),
                name='cart_must_have_owner'
            )
        ]

    def __str__(self):
        if self.user:
            return f"Cart for user ({self.user.get_username()})"
        return f"Guest Cart ({self.session_key})"


class CartItem(TimeStampedModel):
    """Represents a single item (a product variant) within a shopping cart."""
    cart = models.ForeignKey(
        "Cart",
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Cart"),
        help_text=_("The cart to which this item belongs.")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name='cart_items',
        verbose_name=_("Product Variant"),
        help_text=_("The specific product variant being added to the cart.")
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Quantity"),
        help_text=_("The number of units of this product variant in the cart.")
    )

    class Meta:
        verbose_name = _("Cart Item")
        verbose_name_plural = _("Cart Items")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'variant'],
                name='unique_variant_per_cart'
            ),
            models.CheckConstraint(
                check=Q(quantity__gt=0),
                name='positive_cart_quantity_per_item'
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.variant.product.name} ({self.variant.name}) in cart {self.cart_id}"


class Order(TimeStampedModel):
    """Represents a customer's order, containing a snapshot of all relevant information at the time of purchase."""

    class OrderStatusChoices(models.TextChoices):
        PENDING_PAYMENT = 'pending_payment', _("Pending Payment")
        PROCESSING = 'processing', _("Processing")
        SHIPPED = 'shipped', _("Shipped")
        DELIVERED = 'delivered', _("Delivered")
        CANCELLED = 'cancelled', _("Cancelled")
        REFUNDED = 'refunded', _("Refunded")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(
        max_length=120,
        unique=True,
        db_index=True,
        verbose_name=_("Order Number"),
        help_text=_("The unique, human-readable identifier for the order. (Auto-generated)")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_("User"),
        help_text=_("The user who placed the order.")
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatusChoices.choices,
        default=OrderStatusChoices.PENDING_PAYMENT,
        verbose_name=_("Order Status"),
        help_text=_("The current stage of the order in its lifecycle.")
    )
    shipping_address = models.ForeignKey(
        "accounts.Address",
        on_delete=models.PROTECT,
        related_name='shipping_orders',
        verbose_name=_("Shipping Address"),
        help_text=_("This must be a snapshot of the user's address at the time of order.")
    )
    billing_address = models.ForeignKey(
        "accounts.Address",
        on_delete=models.PROTECT,
        related_name='billing_orders',
        null=True,
        blank=True,
        verbose_name=_("Billing Address"),
        help_text=_("This must be a snapshot of the user's address at the time of order. (Optional)")
    )
    subtotal_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Subtotal Price"),
        help_text=_("The total price of all items before shipping and discounts.")
    )
    shipping_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name=_("Shipping Price"),
        help_text=_("The cost of shipping for the order.")
    )
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        verbose_name=_("Discount Amount"),
        help_text=_("The total amount of discounts applied to the order.")
    )
    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Final Price"),
        help_text=_("The final amount to be paid by the customer (subtotal + shipping - discount).")
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_("Customer Notes"),
        help_text=_("Optional notes provided by the customer at checkout. (Optional)")
    )

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=Q(subtotal_price__gte=0),
                name='non_negative_order_subtotal_price'
            ),
            models.CheckConstraint(
                check=Q(shipping_price__gte=0),
                name='non_negative_order_shipping_price'
            ),
            models.CheckConstraint(
                check=Q(discount_amount__gte=0),
                name='non_negative_order_discount_amount'
            ),
            models.CheckConstraint(
                check=Q(final_price__gte=0),
                name='non_negative_order_final_price'
            ),
        ]

    def __str__(self):
        return f"Order {self.order_number}"


class OrderItem(TimeStampedModel):
    """Represents a single item within an order, containing a snapshot of the product variant's details at the time of purchase."""
    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_("Order"),
        help_text=_("The order to which this item belongs.")
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        related_name='order_items',
        null=True,
        verbose_name=_("Product Variant"),
        help_text=_("A reference to the original product variant. Can be null if the variant is deleted.")
    )
    product_title = models.CharField(
        max_length=255,
        verbose_name=_("Product Title"),
        help_text=_("A snapshot of the product's name at the time of purchase.")
    )
    variant_title = models.CharField(
        max_length=255,
        verbose_name=_("Variant Title"),
        help_text=_("A snapshot of the variant's specific name (e.g., 'Red, Large').")
    )
    sku = models.CharField(
        max_length=100,
        verbose_name=_("SKU"),
        help_text=_("A snapshot of the Stock Keeping Unit.")
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Unit Price"),
        help_text=_("The price of a single unit of the item at the time of purchase.")
    )
    quantity = models.PositiveIntegerField(
        verbose_name=_("Quantity"),
        help_text=_("The number of units of this item purchased.")
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Total Price"),
        help_text=_("The total price for this line item (unit_price * quantity).")
    )
    attributes_snapshot = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Attributes Snapshot"),
        help_text=_("A JSON snapshot of the variant's defining attributes at the time of purchase.")
    )

    class Meta:
        verbose_name = _("Order Item")
        verbose_name_plural = _("Order Items")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'variant'],
                condition=Q(variant__isnull=False),
                name='unique_variant_per_order'
            ),
            models.CheckConstraint(
                check=Q(quantity__gt=0),
                name='positive_order_quantity_per_item'
            ),
            models.CheckConstraint(
                check=Q(unit_price__gte=0),
                name='non_negative_order_item_unit_price'
            ),
            models.CheckConstraint(
                check=Q(total_price__gte=0),
                name='non_negative_order_item_total_price'
            ),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product_title} ({self.variant_title})"
