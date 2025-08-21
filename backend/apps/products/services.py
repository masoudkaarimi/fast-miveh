from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from apps.media.services import MediaService
from apps.products.exceptions import OutOfStockError, ProductNotFound
from apps.products.models import Attribute, AttributeValue, Inventory, Price, Product

User = get_user_model()


class ProductService:
    """Handles the logic for fetching and preparing product data for display."""

    def __init__(self, product_slug, request=None):
        self.product_slug = product_slug
        self.product = self._get_product()
        self.request = request

    def _get_product(self):
        """
        Fetches the product instance using an optimized query.
        Raises ProductNotFound if the product does not exist or is not published.
        """
        try:
            product = Product.objects.published().with_details().get(slug=self.product_slug)
            return product
        except Product.DoesNotExist:
            raise ProductNotFound(_("The product with the given slug does not exist or is not active."))

    def get_context_for_detail_page(self):
        """Prepares the context data for rendering a product detail page."""
        active_variants = self.product.variants.active().prefetch_related('prices__currency', 'inventory', 'attributes__attribute', 'media_links__media')
        if not active_variants.exists():
            raise ProductNotFound(_("This product has no available variants."))

        context = {
            'product_id': self.product.id,
            'product_name': self.product.name,
            'product_slug': self.product.slug,
            'description': self.product.description,
            'brand': self.product.brand if (self.product.brand and self.product.brand.is_active) else None,
            'categories': self.product.categories.filter(is_active=True),
            'tags': list(self.product.tags.filter(is_active=True).values_list('name', flat=True)),
            'variants_map': self._get_variants_map(active_variants),
            'options': self._get_configurable_options(active_variants),
            'media': self._get_media_gallery(self.product),
        }
        return context

    def _get_media_gallery(self, obj):
        """Returns a serialized list of media links for the given object."""
        from apps.products.serializers import ProductMediaSerializer

        media_links_qs = MediaService.get_media_links_for(obj)

        return ProductMediaSerializer(media_links_qs, many=True, context={'request': self.request}).data

    def _get_variants_map(self, variants):
        """
        Constructs a dictionary mapping variant IDs to their details.
        e.g., { 101: { 'sku': 'ABC', 'price': 15.99, 'media': [...] } }
        """
        variant_map = {}
        for variant in variants:
            price_info = PricingService(variant).get_price()
            inventory_info = InventoryService(variant)
            serialized_media = self._get_media_gallery(variant)
            attributes = variant.attributes.filter(attribute__is_active=True)

            variant_map[variant.id] = {
                'sku': variant.sku,
                'name': variant.name,
                'is_default': variant.is_default,
                'price': price_info['final_price'],
                'base_price': price_info['base_price'],
                'is_on_sale': price_info['is_on_sale'],
                'discount_amount': price_info['discount_amount'],
                # 'currency_symbol': price_info['currency_symbol'],
                'is_in_stock': inventory_info.is_in_stock(),
                'attributes': {attr.attribute.slug: attr.value for attr in attributes},
                'media': serialized_media
            }
        return variant_map

    def _get_configurable_options(self, variants):
        """
        Extracts all unique, variant-defining attribute values to build the UI selectors,
        considering the entire ProductType hierarchy.
        e.g., { "color": ["Red", "Blue", "Green"], "size": ["S", "M", "L"] }
        """
        options = {}
        product_type = self.product.product_type
        type_hierarchy = product_type.get_ancestors(include_self=True)

        variant_defining_attributes = Attribute.objects.filter(
            producttypeattribute__product_type__in=type_hierarchy,
            is_variant_defining=True,
            is_active=True
        ).distinct()

        for attr in variant_defining_attributes:
            attribute_values_qs = AttributeValue.objects.filter(
                attribute=attr,
                productvariant__in=variants
            ).distinct().order_by('display_order', 'value')
            values = list(attribute_values_qs.values_list('value', flat=True))
            if values:
                options[attr.slug] = values

        return options


class InventoryService:
    """Handles the logic for managing stock levels of product variants."""

    def __init__(self, variant):
        self.variant = variant
        self.inventory, _ = Inventory.objects.get_or_create(variant=self.variant)

    def is_in_stock(self, quantity=1):
        """Checks if the variant is in stock."""
        if not self.inventory.track_inventory:
            return True
        if self.inventory.allow_backorders:
            return True
        return self.inventory.available_quantity >= quantity

    @transaction.atomic
    def decrease_stock(self, quantity):
        """
        Decreases the stock for a variant after a successful order.
        This operation is atomic to prevent race conditions.
        """
        if not self.inventory.track_inventory:
            return

        if not self.is_in_stock(quantity):
            raise OutOfStockError(_("Not enough stock available for this variant."))

        inventory_to_update = Inventory.objects.select_for_update().get(pk=self.inventory.pk)
        if inventory_to_update.quantity < quantity:
            raise OutOfStockError(_("The requested quantity is no longer in stock."))

        inventory_to_update.quantity = F('quantity') - quantity
        inventory_to_update.save(update_fields=['quantity'])
        self.inventory.refresh_from_db()

    @transaction.atomic
    def increase_stock(self, quantity):
        """
        Increases the stock for a variant (e.g., order cancellation, return).
        Triggers notifications if it comes back in stock.
        This operation is atomic to prevent race conditions.
        """
        if not self.inventory.track_inventory or quantity <= 0:
            return

        inventory_to_update = Inventory.objects.select_for_update().get(pk=self.inventory.pk)
        old_quantity = inventory_to_update.available_quantity
        inventory_to_update.quantity = F('quantity') + quantity
        inventory_to_update.save(update_fields=['quantity'])
        self.inventory.refresh_from_db()

        if old_quantity <= 0 < self.inventory.quantity:
            from apps.products.tasks import send_back_in_stock_notifications

            send_back_in_stock_notifications.delay(self.variant.id)


class PricingService:
    """Handles the logic for calculating and retrieving prices for product variants."""

    def __init__(self, variant, user=None):
        self.variant = variant
        self.user = user  # For future use (e.g., customer-group pricing)

    def get_price(self):
        """Calculates the final price for a variant."""
        try:
            # NOTES: In the future, this service will provide a layer for more complex logic (e.g., taxes, multiple currencies, user-specific discounts).

            price_obj = self.variant.prices.first()
            if not price_obj:
                raise Price.DoesNotExist

            return {
                "base_price": price_obj.base_price,
                "final_price": price_obj.current_price,
                "is_on_sale": price_obj.is_on_sale,
                "discount_amount": price_obj.saved_amount,
                # "currency_code": price_obj.currency.code,
                # "currency_symbol": price_obj.currency.symbol,
            }
        except Price.DoesNotExist:
            # Return a default/error state if no price is defined
            return {
                "base_price": 0,
                "final_price": 0,
                "is_on_sale": False,
                "discount_amount": 0,
                # "currency_code": "N/A",
                # "currency_symbol": "",
            }
