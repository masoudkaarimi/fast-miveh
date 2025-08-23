import datetime
import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Cart, CartItem, Order, OrderItem
from apps.products.exceptions import OutOfStockError
from apps.products.models import ProductVariant
from apps.products.services import InventoryService, PricingService

User = get_user_model()


class CartService:
    """Service layer for managing shopping cart operations."""

    def __init__(self, user=None, session_key=None):
        if not user and not session_key:
            raise ValueError("A user or a session_key must be provided.")
        self.user = user
        self.session_key = session_key
        self.cart = self._get_or_create_cart()

    def _get_or_create_cart(self):
        """Retrieves the cart for the current user or session, or creates a new one."""
        lookup_params = {}
        if self.user and self.user.is_authenticated:
            lookup_params['user'] = self.user
        else:
            lookup_params['session_key'] = self.session_key
            lookup_params['user'] = None

        cart, created = Cart.objects.get_or_create(**lookup_params)
        return cart

    def _check_stock(self, variant, quantity):
        """Checks if the requested quantity of a product variant is in stock."""
        inventory_service = InventoryService(variant)
        try:
            if not inventory_service.is_in_stock(quantity):
                raise OutOfStockError(
                    _("Not enough stock for {product}. Only {stock} available.").format(
                        product=variant.name, stock=inventory_service.inventory.available_quantity
                    )
                )
        except OutOfStockError as e:
            raise e

    @transaction.atomic
    def add_item(self, variant_id, quantity=1):
        """Adds a product variant to the cart or updates its quantity if it already exists."""
        if quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")

        variant = ProductVariant.objects.select_related('inventory').get(pk=variant_id)

        self._check_stock(variant, quantity)

        item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            variant=variant,
            defaults={'quantity': quantity}
        )
        if not created:
            new_quantity = item.quantity + quantity
            self._check_stock(variant, new_quantity)
            item.quantity = F('quantity') + quantity
            item.save()

        item.refresh_from_db()
        return item

    def update_item_quantity(self, item_id, quantity):
        """Updates the quantity of a specific item in the cart. If quantity is 0, the item is removed."""
        item = self.cart.items.select_related('variant__inventory').get(pk=item_id)

        if quantity <= 0:
            item.delete()
            return None

        self._check_stock(item.variant, quantity)
        item.quantity = quantity
        item.save(update_fields=['quantity'])
        return item

    def remove_item(self, item_id):
        """Removes an item completely from the cart."""
        self.cart.items.get(pk=item_id).delete()

    def clear(self):
        """Removes all items from the cart."""
        self.cart.items.all().delete()

    def get_data(self):
        """Retrieves the cart data, including items, total items, and subtotal."""
        cart_items = self.cart.items.select_related(
            'variant__product__brand',
            'variant__inventory',
        ).prefetch_related(
            'variant__product__media_links__media',
            'variant__prices'
        )

        items_data = []
        subtotal = 0

        for item in cart_items:
            price_info = PricingService(variant=item.variant).get_price()
            unit_price = price_info.get('final_price', 0)
            line_total = unit_price * item.quantity
            subtotal += line_total
            product = item.variant.product
            image_url = None
            if product.featured_image:
                image_url = product.featured_image.file.url

            items_data.append({
                'id': item.id,
                'variant_id': item.variant.id,
                'product_name': product.name,
                'product_slug': product.slug,
                'variant_name': item.variant.name,
                'sku': item.variant.sku,
                'quantity': item.quantity,
                'unit_price': unit_price,
                'line_total': line_total,
                'image_url': image_url,
            })

        return {
            'id': self.cart.id,
            'items': items_data,
            'total_items': sum(item['quantity'] for item in items_data),
            'subtotal': subtotal
        }


class OrderService:
    """Service layer for managing order creation and processing."""

    def __init__(self, user):
        self.user = user

    def _generate_order_number(self):
        """Generates a unique, human-readable order number. Example: ORD-20250731-ABC12"""
        now = timezone.now()
        date_part = now.strftime('%Y%m%d')
        random_part = str(uuid.uuid4().hex[:5]).upper()
        return f"ORD-{date_part}-{random_part}"

    def _create_address_snapshot(self, address):
        """
        Creates a snapshot of an address to be stored with the order,
        ensuring that future changes to the original address do not affect
        the order history.
        """
        address.pk = None  # Clone the address instance
        address.is_snapshot = True
        address.save()
        return address

    @transaction.atomic
    def create_order_from_cart(self, cart, shipping_address, billing_address=None, notes=""):
        """Creates an order from the provided cart, ensuring all items are in stock."""
        if not cart.items.exists():
            raise ValueError("Cannot create an order from an empty cart.")

        cart_service = CartService(user=self.user, session_key=cart.session_key)
        cart_data = cart_service.get_data()

        # Final Stock Check
        for item_data in cart_data['items']:
            variant = ProductVariant.objects.get(pk=item_data['variant_id'])
            inventory_service = InventoryService(variant)
            if not inventory_service.is_in_stock(item_data['quantity']):
                raise OutOfStockError(_("Item '{product}' went out of stock.").format(product=item_data['product_name']))

        # Create Address Snapshots
        shipping_address_snapshot = self._create_address_snapshot(shipping_address)
        billing_address_snapshot = None
        if billing_address:
            if billing_address.id == shipping_address.id:
                billing_address_snapshot = shipping_address_snapshot
            else:
                billing_address_snapshot = self._create_address_snapshot(billing_address)

        # Create the Order
        order = Order.objects.create(
            user=self.user,
            order_number=self._generate_order_number(),
            shipping_address=shipping_address_snapshot,
            billing_address=billing_address_snapshot,
            subtotal_price=cart_data['subtotal'],
            shipping_price=0,
            discount_amount=0,
            final_price=cart_data['subtotal'],
            notes=notes
        )

        # Create Order Items and Decrease Stock
        for item_data in cart_data['items']:
            variant = ProductVariant.objects.select_related('inventory').get(pk=item_data['variant_id'])
            attributes_snapshot = {
                attr.attribute.name: attr.value
                for attr in variant.attributes.filter(attribute__is_variant_defining=True)
            }
            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_title=item_data['product_name'],
                variant_title=item_data['variant_name'],
                sku=item_data['sku'],
                unit_price=item_data['unit_price'],
                quantity=item_data['quantity'],
                total_price=item_data['line_total'],
                attributes_snapshot=attributes_snapshot
            )
            inventory_service = InventoryService(variant)
            inventory_service.decrease_stock(item_data['quantity'])

        # Clear the Cart
        cart_service.clear()

        return order
