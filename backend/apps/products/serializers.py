from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext as _
from rest_framework import serializers

from apps.core.serializers import CurrencySerializer
from apps.media.models import MediaLink
from apps.media.services import MediaService
from apps.products.models import (
    Attribute,
    AttributeValue,
    BackInStockSubscription,
    Brand,
    Category,
    Inventory,
    Price,
    Product,
    ProductCollection,
    ProductType,
    ProductVariant,
    Tag,
)
from apps.products.services import PricingService


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for the Brand model."""
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = ('id', 'name', 'slug', 'logo_url')

    def get_logo_url(self, obj):
        """Generates the absolute URL for the brand logo."""
        request = self.context.get('request')

        if obj.logo and hasattr(obj.logo, 'url'):
            return request.build_absolute_uri(obj.logo.url) if request else obj.logo.url

        placeholder_url = static('assets/images/placeholders/brand_placeholder.webp')
        return request.build_absolute_uri(placeholder_url) if request else placeholder_url


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'image_url')

    def get_image_url(self, obj):
        """Generates the absolute URL for the category image."""
        request = self.context.get('request')

        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url

        placeholder_url = static('assets/images/placeholders/category_placeholder.webp')
        return request.build_absolute_uri(placeholder_url) if request else placeholder_url


class ProductMediaSerializer(serializers.ModelSerializer):
    """Serializer for media links associated with products."""
    url = serializers.SerializerMethodField()
    alt_text = serializers.CharField(source='media.alt_text', read_only=True)
    media_type = serializers.CharField(source='media.media_type', read_only=True)

    class Meta:
        model = MediaLink
        fields = ('url', 'alt_text', 'media_type', 'is_featured')

    def get_url(self, obj):
        """Generates the absolute URL for the media file."""
        if hasattr(obj, 'media') and obj.media and hasattr(obj.media, 'file') and obj.media.file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.media.file.url) if request else obj.media.file.url
        return None


# class AttributeValueSerializer(serializers.ModelSerializer):
#     """Serializer for the AttributeValue model."""
#
#     class Meta:
#         model = AttributeValue
#         fields = ('id', 'value', 'slug', 'meta')


# class AttributeSerializer(serializers.ModelSerializer):
#     """Serializer for the Attribute model, including its values."""
#     values = AttributeValueSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = Attribute
#         fields = ('id', 'name', 'slug', 'display_type', 'unit', 'is_variant_defining', 'is_filterable', 'values')


# class ProductTypeSerializer(serializers.ModelSerializer):
#     """Serializer for the ProductType model, including its attributes."""
#     attributes = AttributeSerializer(many=True, read_only=True)
#     parent = serializers.PrimaryKeyRelatedField(read_only=True)
#
#     class Meta:
#         model = ProductType
#         fields = ('id', 'name', 'slug', 'parent', 'description', 'attributes')


# class PriceSerializer(serializers.ModelSerializer):
#     """Serializer for the Price model, including currency and sale information."""
#     currency = CurrencySerializer(read_only=True)
#     is_on_sale = serializers.BooleanField(read_only=True)
#     current_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
#
#     class Meta:
#         model = Price
#         fields = ('id', 'currency', 'base_price', 'sale_price', 'is_on_sale', 'current_price',)


# class InventorySerializer(serializers.ModelSerializer):
#     """Serializer for the Inventory model, including stock status and quantities."""
#     is_in_stock = serializers.BooleanField(read_only=True)
#     available_quantity = serializers.IntegerField(read_only=True)
#
#     class Meta:
#         model = Inventory
#         fields = ('id', 'quantity', 'is_in_stock', 'available_quantity', 'allow_backorders')


# class ProductVariantSerializer(serializers.ModelSerializer):
#     """Serializer for the ProductVariant model, including prices, inventory, and attributes."""
#     prices = PriceSerializer(many=True, read_only=True)
#     inventory = InventorySerializer(read_only=True)
#     attributes = AttributeValueSerializer(many=True, read_only=True)
#     media = serializers.SerializerMethodField()
#
#     class Meta:
#         model = ProductVariant
#         fields = ('id', 'sku', 'name', 'unit', 'max_order_quantity', 'is_default', 'media', 'attributes', 'prices', 'inventory')
#
#     def get_media(self, obj):
#         """Gets a list of media items associated with the product variant."""
#         media_links_qs = MediaService.get_media_links_for(obj)
#
#         return ProductMediaSerializer(media_links_qs, many=True, context=self.context).data


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for listing products."""
    price_info = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    variant_name = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()
    unit = serializers.SerializerMethodField()
    inventory_info = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'variant_name', 'slug', 'sku', 'unit', 'short_description', 'featured_image_url', 'media', 'brand', 'tags', 'categories', 'price_info',
                  'inventory_info',)

    def get_brand(self, obj):
        """Gets the active brand for the product."""
        if obj.brand and obj.brand.is_active:
            return BrandSerializer(obj.brand, context=self.context).data
        return None

    def get_categories(self, obj):
        """Gets the active categories for the product."""
        active_categories = obj.categories.filter(is_active=True)
        return CategorySerializer(active_categories, many=True, context=self.context).data

    def get_tags(self, obj):
        """Gets the active tags for the product."""
        return list(obj.tags.filter(is_active=True).values_list('name', flat=True))

    def get_price_info(self, obj):
        """Calculates and returns the price information for the product's default variant."""
        default_variant = obj.default_variant
        if not default_variant:
            return {
                "base_price": 0,
                "final_price": 0,
                "is_on_sale": False,
                "discount_amount": 0,
                "discount_percentage": 0,
                "currency_symbol": "N/A"
            }

        price_data = PricingService(variant=default_variant).get_price()

        if price_data.get('is_on_sale') and price_data.get('base_price', 0) > 0:
            discount = price_data['base_price'] - price_data.get('final_price', 0)
            percentage = round((discount / price_data['base_price']) * 100)
            price_data['discount_percentage'] = percentage
        else:
            price_data['discount_percentage'] = 0

        return price_data

    def get_featured_image_url(self, obj):
        """Generates the absolute URL for the product's featured image."""
        request = self.context.get('request')

        if featured_image := obj.featured_image:
            return request.build_absolute_uri(featured_image.file.url) if request else featured_image.file.url

        placeholder_url = static('assets/images/placeholders/product_placeholder.webp')
        return request.build_absolute_uri(placeholder_url) if request else placeholder_url

    def get_media(self, obj):
        """Gets a list of media items associated with the product."""
        media_links_qs = MediaService.get_media_links_for(obj)

        return ProductMediaSerializer(media_links_qs, many=True, context=self.context).data

    def get_variant_name(self, obj):
        """Gets the name of the product's default variant."""
        if default_variant := obj.default_variant:
            return default_variant.name
        return None

    def get_sku(self, obj):
        """Gets the SKU of the product's default variant."""
        if default_variant := obj.default_variant:
            return default_variant.sku
        return None

    def get_inventory_info(self, obj):
        """Calculates and returns the inventory information for the product's default variant."""
        if not (default_variant := obj.default_variant):
            return {
                "quantity": 0,
                "max_quantity": 0,
                "is_in_stock": False,
                "allow_backorders": False
            }

        if hasattr(default_variant, 'inventory'):
            inventory = default_variant.inventory
            available_qty = inventory.available_quantity
            max_qty_allowed = available_qty

            if default_variant.max_order_quantity is not None and default_variant.max_order_quantity > 0:
                max_qty_allowed = min(available_qty, default_variant.max_order_quantity)

            return {
                "quantity": available_qty,
                "max_quantity": max_qty_allowed,
                "is_in_stock": inventory.is_in_stock,
                "allow_backorders": inventory.allow_backorders
            }

        return {
            "quantity": 0,
            "max_quantity": 0,
            "is_in_stock": False,
            "allow_backorders": False
        }

    def get_unit(self, obj):
        """Returns the unit of the product's default variant."""
        if default_variant := obj.default_variant:
            return default_variant.unit
        return _("Item")


class ProductDetailSerializer(serializers.Serializer):
    """Serializer for detailed product information, including variants and pricing."""
    product_id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField(read_only=True)
    product_slug = serializers.SlugField(read_only=True)
    description = serializers.CharField(read_only=True)
    brand = BrandSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    tags = serializers.ListField(child=serializers.CharField(), read_only=True)
    variants_map = serializers.DictField(read_only=True)
    options = serializers.DictField(read_only=True)
    media = serializers.ListField(child=serializers.DictField(), read_only=True)


class ProductCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCollection
        fields = ['id', 'name', 'slug', 'description', 'image', ]


class ProductCollectionDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = ProductCollection
        fields = ['id', 'name', 'slug', 'description', 'image', 'products', ]


class BackInStockSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for managing back-in-stock subscriptions for product variants."""
    variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all(), write_only=True)
    email = serializers.EmailField(required=False, write_only=True)

    class Meta:
        model = BackInStockSubscription
        fields = ('variant', 'email')

    def validate_variant(self, variant_object):
        if hasattr(variant_object, 'inventory') and variant_object.inventory.is_in_stock:
            raise serializers.ValidationError(_("This product is already in stock."))

        return variant_object

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated and not data.get('email'):
            raise serializers.ValidationError({"email": _("An email address is required for guest subscribers.")})
        return data

    def create(self, validated_data):
        variant_object = validated_data.get('variant')
        user = self.context['request'].user
        lookup_params = {'variant': variant_object}

        if user.is_authenticated:
            lookup_params['user'] = user
        else:
            lookup_params['email'] = validated_data['email']

        # Prevent duplicate subscriptions
        instance, created = BackInStockSubscription.objects.get_or_create(**lookup_params)

        # If a user re-subscribes after a notification was already sent, reactivate it.
        if not created and instance.status == BackInStockSubscription.StatusChoices.SENT:
            instance.status = BackInStockSubscription.StatusChoices.PENDING
            instance.save(update_fields=['status'])

        return instance
