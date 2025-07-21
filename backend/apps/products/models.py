from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.templatetags.static import static
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _

from mptt.fields import TreeManyToManyField
from mptt.models import MPTTModel, TreeForeignKey

from apps.common.models import TimeStampedModel
from apps.common.utils import GenerateUploadPath
from apps.products.managers import ProductQuerySet, ProductVariantQuerySet
from apps.common.validators import FileSizeValidator, FileExtensionValidator


class Currency(TimeStampedModel):
    """
    Represents a currency supported by the store.
    e.g., IRR, USD, EUR
    """
    code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name=_("currency code"),
        help_text=_("The ISO 4217 currency code, e.g., 'IRR', 'USD'.")
    )
    name = models.CharField(
        max_length=50,
        verbose_name=_("currency name"),
        help_text=_("The full name of the currency, e.g., 'Iranian Rial'.")
    )
    symbol = models.CharField(
        max_length=5,
        verbose_name=_("currency symbol"),
        help_text=_("The symbol for the currency, e.g., '﷼', '$'.")
    )
    exchange_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        default=1.0,
        verbose_name=_("exchange rate"),
        help_text=_("The exchange rate relative to the store's base currency.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Controls whether this currency is available for customers.")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("is default"),
        help_text=_("Marks this as the default currency for the store. Only one can be default.")
    )

    class Meta:
        verbose_name = _("Currency")
        verbose_name_plural = _("Currencies")
        ordering = ['code']

    def __str__(self):
        return self.code

    def save(self, *args, **kwargs):
        # Ensure only one currency is marked as default.
        if self.is_default:
            Currency.objects.filter(is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


class Category(MPTTModel, TimeStampedModel):
    """
    Represents a product category, supporting a hierarchical structure.
    e.g., Electronics > Laptops > Gaming Laptops
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("category name"),
        help_text=_("The name of the category, e.g., 'Electronics', 'Laptops'."),
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("category slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        verbose_name=_("parent category"),
        help_text=_("The parent category for hierarchical categorization. Leave blank for top-level categories.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("A brief description of the category.")
    )
    image = models.ImageField(
        upload_to=GenerateUploadPath(folder='categories', sub_path='images/'),
        blank=True,
        null=True,
        validators=[
            FileSizeValidator(max_size_mb=settings.MAX_IMAGE_UPLOAD_SIZE_MB),
            FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)
        ],
        verbose_name=_("image"),
        help_text=_(
            'An image representing the category.<br />'
            'Supported formats: <b>{allowed_image_extensions}</b>.<br />'
            'Maximum file size: <b>{max_size}MB</b>.'
        ).format(
            allowed_image_extensions=', '.join(settings.ALLOWED_IMAGE_EXTENSIONS),
            max_size=settings.MAX_IMAGE_UPLOAD_SIZE_MB
        )
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("The order in which this category appears in listings. Lower numbers appear first.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Controls whether the category is visible to customers.")
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:category_detail', kwargs={'slug': self.slug})

    def get_image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return static('assets/images/placeholders/category_placeholder.webp')


class Brand(TimeStampedModel):
    """
    Represents a product brand or manufacturer.
    e.g., Apple, Sony, Nike
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("brand name"),
        help_text=_("The name of the brand, e.g., 'Apple', 'Sony', 'Nike'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("brand slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    logo = models.ImageField(
        upload_to=GenerateUploadPath(folder='brands', sub_path='logos/'),
        blank=True,
        null=True,
        validators=[
            FileSizeValidator(max_size_mb=settings.MAX_IMAGE_UPLOAD_SIZE_MB),
            FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)
        ],
        verbose_name=_("logo"),
        help_text=_(
            'A logo image for the brand.<br />'
            'Supported formats: <b>{allowed_image_extensions}</b>.<br />'
            'Maximum file size: <b>{max_size}MB</b>.'
        ).format(
            allowed_image_extensions=', '.join(settings.ALLOWED_IMAGE_EXTENSIONS),
            max_size=settings.MAX_IMAGE_UPLOAD_SIZE_MB
        )
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("A brief description of the brand, its history, and values.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("The order in which this brand appears in listings. Lower numbers appear first.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Controls whether the brand is visible to customers.")
    )

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:brand_detail', kwargs={'slug': self.slug})

    def get_logo_url(self):
        if self.logo and hasattr(self.logo, 'url'):
            return self.logo.url
        return static('assets/images/placeholders/brand_placeholder.webp')


class Tag(TimeStampedModel):
    """
    Represents a tag for non-hierarchical product grouping.
    e.g., "New Arrival", "On Sale", "Organic"
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("tag name"),
        help_text=_("The name of the tag, e.g., 'New Arrival', 'On Sale', 'Organic'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("tag slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Controls whether the tag is visible to customers.")
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('products:tag_detail', kwargs={'slug': self.slug})


class Attribute(TimeStampedModel):
    """
    Defines an attribute's specification.
    e.g., Color, Size, Storage Capacity, RAM.
    """

    class AttributeTypeChoices(models.TextChoices):
        TEXT = 'text', _('Text')
        NUMBER = 'number', _('Number')
        BOOLEAN = 'boolean', _('Boolean')
        DATETIME = 'datetime', _('DateTime')

    class DisplayTypeChoices(models.TextChoices):
        DROPDOWN = 'dropdown', _('Dropdown')
        COLOR_SWATCH = 'color_swatch', _('Color Swatch')
        TEXT_INPUT = 'text_input', _('Text Input')
        RADIO_BUTTON = 'radio_button', _('Radio Button')

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("attribute name"),
        help_text=_("The internal name of the attribute, e.g., 'Color', 'Size'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("attribute slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    attribute_type = models.CharField(
        max_length=20,
        choices=AttributeTypeChoices.choices,
        default=AttributeTypeChoices.TEXT,
        verbose_name=_("data type"),
        help_text=_("The underlying data attribute type for the attribute's values.")
    )
    display_type = models.CharField(
        max_length=50,
        choices=DisplayTypeChoices.choices,
        default=DisplayTypeChoices.DROPDOWN,
        verbose_name=_("display type"),
        help_text=_("How this attribute should be displayed on the product page.")
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("unit of measurement"),
        help_text=_("The unit for this attribute, if applicable (e.g., 'kg', 'cm', 'GB').")
    )
    help_text = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("help text"),
        help_text=_("Additional instructions or information for this attribute shown to the user.")
    )
    is_variant_defining = models.BooleanField(
        default=False,
        verbose_name=_("is variant defining"),
        help_text=_("If true, this attribute is used to create product variants (e.g., color, size).")
    )
    is_filterable = models.BooleanField(
        default=False,
        verbose_name=_("is filterable"),
        help_text=_("If true, this attribute can be used for filtering products.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Controls whether this attribute is globally active and can be used.")
    )

    class Meta:
        verbose_name = _("Attribute")
        verbose_name_plural = _("Attributes")
        ordering = ['name']

    def __str__(self):
        return self.name


class AttributeValue(TimeStampedModel):
    """
    Defines a specific value for an attribute.
    e.g., 'Red' for 'Color', or 'Large' for 'Size'.
    """
    attribute = models.ForeignKey(
        "Attribute",
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name=_("attribute"),
        help_text=_("The attribute this value belongs to, e.g., 'Color', 'Size'.")
    )
    value = models.CharField(
        max_length=255,
        verbose_name=_("value"),
        help_text=_("The actual value, e.g., 'Red', 'XL', '256GB'.")
    )
    slug = models.SlugField(
        max_length=255,
        allow_unicode=True,
        verbose_name=_("value slug"),
        help_text=_("A URL-friendly version of the value. Should be unique per attribute.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("The order in which this value appears in lists. Lower numbers appear first.")
    )
    meta = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("meta data"),
        help_text=_("Extra data, e.g., {'hex_code': '#FF0000'} for a color.")
    )

    class Meta:
        verbose_name = _("Attribute Value")
        verbose_name_plural = _("Attribute Values")
        ordering = ['display_order', 'value']
        unique_together = [['attribute', 'value'], ['attribute', 'slug']]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductType(TimeStampedModel):
    """
    Defines a "blueprint" for a product, grouping a set of attributes.
    e.g., A "T-Shirt" product type.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("product type name"),
        help_text=_("A name for the product type, e.g., 'T-Shirt', 'Smartphone'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("product type slug")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("An optional description for this product type for internal reference.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("The order in which this product type appears in lists.")
    )
    attributes = models.ManyToManyField(
        "Attribute",
        through='ProductTypeAttribute',
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Attributes associated with this product type.")
    )

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class ProductTypeAttribute(TimeStampedModel):
    """
    Through model to store metadata about the relationship
    between a ProductType and an Attribute.
    """
    product_type = models.ForeignKey(
        "ProductType",
        on_delete=models.CASCADE,
        verbose_name=_("product type"),
        help_text=_("The product type this attribute belongs to, e.g., 'T-Shirt', 'Smartphone'.")
    )
    attribute = models.ForeignKey(
        "Attribute",
        on_delete=models.CASCADE,
        verbose_name=_("attribute"),
        help_text=_("The attribute associated with this product type, e.g., 'Color', 'Size'.")
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("is required"),
        help_text=_("Indicates if this attribute is required for products of this type.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("The order in which this attribute is displayed for this product type.")
    )

    class Meta:
        verbose_name = _("Product Type Attribute")
        verbose_name_plural = _("Product Type Attributes")
        unique_together = [['product_type', 'attribute']]
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return f"{self.product_type.name} - {self.attribute.name}"


class Product(TimeStampedModel):
    """
    Represents the conceptual product or product template.
    It holds all the shared information among its variants.
    e.g., "Apple iPhone 15 Pro", "Nike Air Max 90"
    """
    product_type = models.ForeignKey(
        "ProductType",
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_("product type"),
        help_text=_("The type of the product, which defines its attributes.")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("product name"),
        help_text=_("The main name of the product.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("product slug"),
        help_text=_("A unique, URL-friendly version of the product name.")
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("short description"),
        help_text=_("A brief summary shown in product listings and SEO results.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("A detailed description of the product for the product page.")
    )
    brand = models.ForeignKey(
        "Brand",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_("brand"),
        help_text=_("The brand of the product, if any.")
    )
    categories = TreeManyToManyField(
        "Category",
        blank=True,
        related_name='products',
        verbose_name=_("categories"),
        help_text=_("The categories this product belongs to.")
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        related_name='products',
        verbose_name=_("tags"),
        help_text=_("Tags for flexible, non-hierarchical grouping.")
    )
    media_links = GenericRelation(
        'media.MediaLink',
        verbose_name=_("media links"),
        help_text=_("Links to media files (images, videos) associated with this product.")
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Published At"),
        help_text=_("The date and time this product will become visible. If blank, it's considered published upon activation.")
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("is active"),
        help_text=_("Designates whether this product should be visible in the store. Use this for drafts or archives.")
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})

    @cached_property  # For performance optimization
    def default_variant(self):
        """
        Returns the default variant for the product.
        Caches the result for the lifetime of the request to avoid extra queries.
        """
        return self.variants.filter(is_active=True, is_default=True).first()

        # The get_featured_image method can now be written cleanly

    @cached_property
    def featured_image(self):
        featured_link = self.media_links.filter(is_featured=True).first()
        if featured_link and featured_link.media.media_type == 'image':
            return featured_link.media
        return None


class ProductVariant(TimeStampedModel):
    """
    Represents a specific, sellable version of a Product.
    This is the item that has a price, stock, and can be added to a cart.
    e.g., "Apple iPhone 15 Pro - 256GB - Blue"
    """
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_("product"),
        help_text=_("The parent product this variant belongs to.")
    )
    name = models.CharField(
        max_length=255,
        blank=True,  # Can be auto-generated
        verbose_name=_("variant name"),
        help_text=_("A specific name for this variant, e.g., 'Large, Red'. Can be auto-generated.")
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("SKU (Stock Keeping Unit)"),
        help_text=_("A unique identifier for this variant for inventory management.")
    )
    upc = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("UPC (Universal Product Code)"),
        help_text=_("The barcode number for this variant.")
    )
    attributes = models.ManyToManyField(
        "AttributeValue",
        verbose_name=_("attributes"),
        help_text=_("The specific attribute values that define this variant (e.g., Color: Red, Size: Large).")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("is default"),
        help_text=_("If true, this variant is shown by default on the product page.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Controls whether this specific variant is available for sale.")
    )

    objects = ProductVariantQuerySet.as_manager()

    class Meta:
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Product Variants")
        ordering = ['-created_at']
        # A variant is unique by its product and the combination of its attributes.
        # This is enforced at the application level, not as a DB constraint here
        # due to the complexity of enforcing uniqueness on a ManyToManyField.

    def __str__(self):
        return f"{self.product.name} - {self.name or self.sku}"

    def save(self, *args, **kwargs):
        if not self.name:
            # Auto-generate a name if it's blank
            self.name = self.sku
        super().save(*args, **kwargs)


class ProductCollection(TimeStampedModel):
    """
    Represents a curated collection of products for merchandising.
    e.g., "Summer Sale", "Homepage Featured", "Staff Picks"
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("collection name"),
        help_text=_("The name of the collection, e.g., 'Summer Sale', 'Homepage Featured'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("collection slug"),
        help_text=_("A unique, URL-friendly version of the collection name.")
    )
    products = models.ManyToManyField(
        Product,
        through='ProductCollectionEntry',
        related_name='collections',
        blank=True,
        verbose_name=_("products"),
        help_text=_("The products included in this collection. Use the through model for custom sorting.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("description"),
        help_text=_("A description for the collection page (for SEO and users).")
    )
    image = models.ImageField(
        upload_to=GenerateUploadPath(folder='collections', sub_path='images/'),
        blank=True,
        null=True,
        verbose_name=_("image"),
        validators=[
            FileSizeValidator(max_size_mb=settings.MAX_IMAGE_UPLOAD_SIZE_MB),
            FileExtensionValidator(allowed_extensions=settings.ALLOWED_IMAGE_EXTENSIONS)
        ],
        help_text=_(
            'An image representing the collection.<br />'
            'Supported formats: <b>{allowed_image_extensions}</b>.<br />'
            'Maximum file size: <b>{max_size}MB</b>.'
        ).format(
            allowed_image_extensions=', '.join(settings.ALLOWED_IMAGE_EXTENSIONS),
            max_size=settings.MAX_IMAGE_UPLOAD_SIZE_MB
        )
    )
    start_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("start date"),
        help_text=_("The date and time when the collection becomes active.")
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("end date"),
        help_text=_("The date and time when the collection expires.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("The order in which this collection appears in listings. Lower numbers appear first.")
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("is active"),
        help_text=_("Manually activate or deactivate this collection.")
    )

    class Meta:
        verbose_name = _("Product Collection")
        verbose_name_plural = _("Product Collections")
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('products:collection_detail', kwargs={'slug': self.slug})


class ProductCollectionEntry(TimeStampedModel):
    """
    Through model to handle the relationship between a Product and a ProductCollection,
    allowing for custom sorting.
    """
    collection = models.ForeignKey(
        ProductCollection,
        on_delete=models.CASCADE,
        verbose_name=_("product collection"),
        help_text=_("The collection of this product entry belongs to.")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("product"),
        help_text=_("The product that is part of this collection entry.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("display order"),
        help_text=_("The order in which this product appears in the collection. Lower numbers appear first.")
    )

    class Meta:
        verbose_name = _("Product Collection Entry")
        verbose_name_plural = _("Product Collection Entries")
        ordering = ['display_order', '-created_at']
        unique_together = [['collection', 'product']]


class Price(TimeStampedModel):
    """
    Represents the pricing information for a specific ProductVariant.
    """
    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name=_("product variant"),
        help_text=_("The product variant this price applies to.")
    )
    currency = models.ForeignKey(
        "Currency",
        on_delete=models.PROTECT,  # Prevent deleting a currency that is in use
        related_name='prices',
        verbose_name=_("currency"),
        help_text=_("The currency in which this price is expressed. Must be an active currency.")
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("base price")
    )
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name=_("sale price"),
        help_text=_("The discounted price during a sale. If not set, the base price is used.")
    )
    sale_start_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("sale start date"),
        help_text=_("The date and time when the sale starts. If not set, the sale is considered active immediately.")
    )
    sale_end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("sale end date"),
        help_text=_("The date and time when the sale ends. If not set, the sale is considered ongoing until manually changed.")
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name=_("cost price"),
        help_text=_("The cost price of the variant, used for profit calculations. If not set, profit cannot be calculated.")
    )

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        unique_together = [['variant', 'currency']]
        ordering = ['currency__code']

    def __str__(self):
        return f"{self.variant} - {self.base_price} {self.currency.code}"

    @property
    def is_on_sale(self):
        """Checks if the sale price is currently active."""
        now = timezone.now()
        if not self.sale_price:
            return False

        starts_in_past = self.sale_start_date is None or self.sale_start_date <= now
        ends_in_future = self.sale_end_date is None or self.sale_end_date >= now

        return starts_in_past and ends_in_future

    @property
    def current_price(self):
        """Returns the active price (sale price if applicable, otherwise base price)."""
        return self.sale_price if self.is_on_sale else self.base_price

    @property
    def is_free(self):
        """A convenience property to check if the variant is free."""
        return self.current_price <= 0

    @property
    def saved_amount(self):
        """Calculates the amount saved during a sale."""
        if self.is_on_sale:
            return self.base_price - self.current_price
        return 0


class Inventory(TimeStampedModel):
    """
    Represents the stock and inventory information for a specific ProductVariant.
    """
    variant = models.OneToOneField(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name=_("product variant"),
        help_text=_("The product variant this inventory record applies to.")
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("quantity on hand"),
        help_text=_("The actual number of items in stock.")
    )
    reserved_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("reserved quantity"),
        help_text=_("The number of items held in active carts or pending orders.")
    )
    threshold = models.PositiveIntegerField(
        default=10,
        verbose_name=_("low stock threshold"),
        help_text=_("When available stock reaches this level, a notification can be triggered.")
    )
    track_inventory = models.BooleanField(
        default=True,
        verbose_name=_("track inventory"),
        help_text=_("If false, stock levels will not be tracked for this variant.")
    )
    allow_backorders = models.BooleanField(
        default=False,
        verbose_name=_("allow backorders"),
        help_text=_("If true, customers can purchase this variant even if it is out of stock.")
    )

    class Meta:
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventories")

    def __str__(self):
        return f"Inventory for {self.variant}"

    @property
    def available_quantity(self):
        """Calculates the real-time available stock."""
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def is_in_stock(self):
        """Checks if the variant is considered in stock."""
        if not self.track_inventory:
            return True
        return self.available_quantity > 0

    @property
    def is_low_stock(self):
        """Checks if the variant is at or below the low stock threshold."""
        if not self.track_inventory:
            return False
        return self.available_quantity <= self.threshold
