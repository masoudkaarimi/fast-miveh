from rest_framework import serializers

from apps.products.services import PricingService
from apps.products.models import Product, Brand, Category, Tag, Currency, AttributeValue, Attribute, ProductType, Price, Inventory, ProductVariant


# --- Foundational Model Serializers ---
class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for the Currency model."""

    class Meta:
        model = Currency
        fields = ('id', 'code', 'name', 'symbol')


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for the Brand model."""

    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'get_logo_url')


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'get_image_url')


class TagSerializer(serializers.ModelSerializer):
    """Serializer for the Tag model."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


# --- Attribute and ProductType Serializers ---
class AttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for AttributeValue, showing its value and meta data."""

    class Meta:
        model = AttributeValue
        fields = ('id', 'value', 'meta')


class AttributeSerializer(serializers.ModelSerializer):
    """Serializer for Attribute, including its possible values."""
    values = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = Attribute
        fields = ('id', 'name', 'slug', 'display_type', 'values')


class ProductTypeSerializer(serializers.ModelSerializer):
    """Serializer for ProductType, showing its associated attributes."""
    attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = ProductType
        fields = ('id', 'name', 'slug', 'attributes')


# --- Price and Inventory Serializers ---
class PriceSerializer(serializers.ModelSerializer):
    """Serializer for the Price model, showing all price fields."""
    currency = CurrencySerializer(read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    current_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Price
        fields = ('id', 'currency', 'base_price', 'sale_price', 'is_on_sale', 'current_price',)


class InventorySerializer(serializers.ModelSerializer):
    """Serializer for the Inventory model."""
    is_in_stock = serializers.BooleanField(read_only=True)
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Inventory
        fields = ('id', 'quantity', 'is_in_stock', 'available_quantity', 'allow_backorders')


# --- Core Product and Variant Serializers ---
class ProductVariantSerializer(serializers.ModelSerializer):
    """
    A detailed serializer for the ProductVariant model, nesting price,
    inventory, and attribute information.
    """
    prices = PriceSerializer(many=True, read_only=True)
    inventory = InventorySerializer(read_only=True)
    attributes = AttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'name', 'is_default', 'attributes', 'prices', 'inventory')


class ProductListSerializer(serializers.ModelSerializer):
    """
    A lightweight serializer for representing products in a list view.
    Includes essential information like name, price, and featured image.
    """
    price_info = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()
    brand = BrandSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'slug', 'short_description', 'brand', 'price_info', 'featured_image_url',)

    @staticmethod
    def get_price_info(obj: Product) -> dict:
        """
        Gets the price information for the product's default variant.
        """
        default_variant = obj.default_variant
        if default_variant:
            # Use the PricingService to get consistent price data
            return PricingService(variant=default_variant).get_price()
        # Return a default structure if there's no default variant
        return {
            "base_price": 0,
            "final_price": 0,
            "is_on_sale": False,
            "currency_symbol": "N/A",
        }

    def get_featured_image_url(self, obj: Product) -> str | None:
        """
        Gets the URL for the product's featured image.
        """
        featured_image = obj.featured_image
        if featured_image:
            # Check if the request context is available to build a full URL
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(featured_image.file.url)
            return featured_image.file.url
        return None


# --- The Main Detail Page Serializer (Service-Driven) ---
class ProductDetailSerializer(serializers.Serializer):
    """
    Read-only serializer for the product detail page, based on the context
    generated by ProductService. This defines the final API output structure.
    """
    product_id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    product_slug = serializers.SlugField(read_only=True)
    description = serializers.CharField(read_only=True)
    brand = serializers.CharField(read_only=True, allow_null=True)
    categories = serializers.ListField(child=serializers.CharField(), read_only=True)

    # These fields contain the complex, nested data prepared by the service
    variants_map = serializers.DictField(read_only=True)
    options = serializers.DictField(read_only=True)
    media = serializers.ListField(child=serializers.DictField(), read_only=True)
