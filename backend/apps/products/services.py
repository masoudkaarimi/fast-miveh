from typing import Dict, Any, List

from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.products.exceptions import ProductNotFound, OutOfStockError
from apps.products.models import Product, ProductVariant, Price, Inventory

User = get_user_model()


class ProductService:
    """Handles the logic for fetching and preparing product data for display."""

    def __init__(self, product_slug: str):
        self.product_slug = product_slug
        self.product = self._get_product()

    def _get_product(self) -> Product:
        """
        Fetches the product instance using an optimized query.
        Raises ProductNotFound if the product does not exist or is not published.
        """
        try:
            # Use the optimized manager method we created
            product = Product.objects.published().with_details().get(slug=self.product_slug)
            return product
        except Product.DoesNotExist:
            raise ProductNotFound(_("The product with the given slug does not exist or is not active."))

    def get_context_for_detail_page(self) -> Dict[str, Any]:
        """
        Constructs a complete dictionary (context) required to render
        the product detail page on the frontend.

        This is the main orchestrator method.
        """
        active_variants = self.product.variants.active()

        if not active_variants.exists():
            """If there are no active variants, we raise an error."""
            raise ProductNotFound(_("This product has no available variants."))

        # The data structure we will send to the frontend
        context = {
            'product_id': self.product.id,
            'product_name': self.product.name,
            'product_slug': self.product.slug,
            'description': self.product.description,
            'brand': self.product.brand.name if self.product.brand else None,
            'categories': [cat.name for cat in self.product.categories.all()],
            'variants_map': self._get_variants_map(active_variants),
            'options': self._get_configurable_options(active_variants),
            'media': self._get_media_gallery(),
        }
        return context

    @staticmethod
    def _get_variants_map(variants: List[ProductVariant]) -> Dict[int, Dict[str, Any]]:
        """
        Creates a map of variant data, keyed by variant ID for easy lookup on the frontend.
        e.g., { 101: { 'sku': 'ABC', 'price': 15.99, 'in_stock': True, 'attributes': {'Color': 'Red', 'Size': 'L'} } }
        """
        variant_map = {}
        for variant in variants:
            price_info = PricingService(variant).get_price()
            inventory_info = InventoryService(variant)

            variant_map[variant.id] = {
                'sku': variant.sku,
                'name': variant.name,
                'is_default': variant.is_default,
                'price': price_info['final_price'],
                'base_price': price_info['base_price'],
                'is_on_sale': price_info['is_on_sale'],
                'discount_amount': price_info['discount_amount'],
                'currency_symbol': price_info['currency_symbol'],
                'is_in_stock': inventory_info.is_in_stock(),
                'attributes': {attr.attribute.name: attr.value for attr in variant.attributes.all()}
            }
        return variant_map

    def _get_configurable_options(self, variants: List[ProductVariant]) -> Dict[str, list]:
        """
        Extracts all unique, variant-defining attribute values to build the UI selectors.
        e.g., { "Color": ["Red", "Blue", "Green"], "Size": ["S", "M", "L"] }
        """
        options = {}
        # We only care about attributes that define a variant from the ProductType
        variant_defining_attributes = self.product.product_type.attributes.filter(is_variant_defining=True)

        for attr in variant_defining_attributes:
            # Get all unique values for this attribute across all active variants of this product
            values = set(variants.filter(attributes__attribute=attr).values_list('attributes__value', flat=True))
            if values:
                options[attr.name] = sorted(list(values))
        return options

    def _get_media_gallery(self) -> list:
        """Prepares a list of media items (images, videos) associated with the product."""

        media_items = []
        # The logic will fetch from the MediaLink model related to the product
        for media_link in self.product.media_links.all().order_by('display_order'):
            media_items.append({
                'url': media_link.media.file.url,
                'alt_text': media_link.media.alt_text,
                'type': media_link.media.media_type,
                'is_featured': media_link.is_featured,
            })
        return media_items


class InventoryService:
    """Handles all stock-related operations for a product variant."""

    def __init__(self, variant: ProductVariant):
        self.variant = variant
        self.inventory, _ = Inventory.objects.get_or_create(variant=self.variant)

    def is_in_stock(self, quantity: int = 1) -> bool:
        """
        Checks if the required quantity is available for purchase.
        Considers backorders.
        """
        if not self.inventory.track_inventory:
            return True
        if self.inventory.allow_backorders:
            return True
        return self.inventory.available_quantity >= quantity

    @transaction.atomic
    def decrease_stock(self, quantity: int):
        """
        Decreases the stock for a variant after a successful order.
        This operation is atomic to prevent race conditions.
        """
        if not self.inventory.track_inventory:
            return

        if not self.is_in_stock(quantity):
            raise OutOfStockError(_("Not enough stock available for this variant."))

        # Use select_for_update to lock the row during the transaction
        inventory_to_update = Inventory.objects.select_for_update().get(pk=self.inventory.pk)
        inventory_to_update.quantity -= quantity
        inventory_to_update.save(update_fields=['quantity'])

    @transaction.atomic
    def increase_stock(self, quantity: int):
        """Increases the stock for a variant (e.g., order cancellation, return)."""
        if not self.inventory.track_inventory:
            return

        inventory_to_update = Inventory.objects.select_for_update().get(pk=self.inventory.pk)
        inventory_to_update.quantity += quantity
        inventory_to_update.save(update_fields=['quantity'])


class PricingService:
    """Handles all price calculation logic for a product variant."""

    def __init__(self, variant: ProductVariant, user: User = None):
        self.variant = variant
        self.user = user  # For future use (e.g., customer-group pricing)

    def get_price(self) -> Dict[str, Any]:
        """
        Calculates the final price for a variant.
        Returns a dictionary with all relevant price components.
        """
        # For now, we delegate to the model's properties.
        # This service provides a layer for future, more complex logic (e.g., taxes, user-specific discounts).
        try:
            # Assuming a single currency for now. This can be extended.
            price_obj = self.variant.prices.get()  # This might fail if you have multiple currencies
            return {
                "base_price": price_obj.base_price,
                "final_price": price_obj.current_price,
                "is_on_sale": price_obj.is_on_sale,
                "discount_amount": price_obj.saved_amount,
                "currency_code": price_obj.currency.code,
                "currency_symbol": price_obj.currency.symbol,
            }
        except Price.DoesNotExist:
            # Return a default/error state if no price is defined
            return {
                "base_price": 0,
                "final_price": 0,
                "is_on_sale": False,
                "discount_amount": 0,
                "currency_code": "N/A",
                "currency_symbol": "",
            }
        except Price.MultipleObjectsReturned:
            # Handle cases with multiple currencies, e.g., return the default one.
            price_obj = self.variant.prices.get(currency__is_default=True)
            return {
                "base_price": price_obj.base_price,
                "final_price": price_obj.current_price,
                "is_on_sale": price_obj.is_on_sale,
                "discount_amount": price_obj.saved_amount,
                "currency_code": price_obj.currency.code,
                "currency_symbol": price_obj.currency.symbol,
            }
