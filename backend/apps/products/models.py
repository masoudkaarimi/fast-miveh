from functools import cached_property

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeManyToManyField
from mptt.models import MPTTModel, TreeForeignKey

from apps.common.models import TimeStampedModel
from apps.common.utils import GenerateUploadPath
from apps.common.validators import FileExtensionValidator, FileSizeValidator
from apps.media.models import Media
from apps.products.managers import ProductQuerySet, ProductVariantQuerySet


class Category(MPTTModel, TimeStampedModel):
    """
    Represents a product category, supporting a hierarchical structure.
    e.g., Electronics > Laptops > Gaming Laptops
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("Category Name"),
        help_text=_("The name of the category, e.g., 'Electronics', 'Laptops'."),
    )
    slug = models.SlugField(
        max_length=255,
        allow_unicode=True,
        verbose_name=_("Category Slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        verbose_name=_("Parent Category"),
        help_text=_("The parent category for hierarchical categorization. Leave blank for top-level categories.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of the category.")
    )
    image = models.FileField(
        upload_to=GenerateUploadPath(base_path='uploads/categories/'),
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
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ['display_order', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent'],
                name='unique_category_name_in_parent'
            ),
            models.UniqueConstraint(
                fields=['slug', 'parent'],
                name='unique_category_slug_in_parent'
            )
        ]

    def __str__(self):
        return self.name

    # def get_full_path(self):
    #     """Returns the full hierarchical path as a string."""
    #     ancestors = self.get_ancestors(include_self=True)
    #     return " > ".join([ancestor.name for ancestor in ancestors])
    #
    # @property
    # def is_leaf(self):
    #     """Returns True if the category has no children."""
    #     return not self.get_children().exists()
    #
    # @property
    # def product_count(self):
    #     """Returns the number of products in this category and its descendants."""
    #     return self.products.filter(is_active=True).count() + \
    #         self.get_descendants().aggregate(
    #             total=models.Count('products', filter=models.Q(products__is_active=True))
    #         )['total'] or 0


class Brand(TimeStampedModel):
    """
    Represents a product brand or manufacturer.
    e.g., Apple, Sony, Nike
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Brand Name"),
        help_text=_("The name of the brand, e.g., 'Apple', 'Sony', 'Nike'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Brand Slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    logo = models.FileField(
        upload_to=GenerateUploadPath(base_path='uploads/brands/'),
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
        verbose_name=_("Description"),
        help_text=_("A brief description of the brand.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
    )

    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    """
    Represents a tag for product grouping.
    e.g., "New", "On Sale", "Organic"
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Tag Name"),
        help_text=_("The name of the tag, e.g., 'New', 'On Sale', 'Organic'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Tag Slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ['-created_at']

    def __str__(self):
        return self.name


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
        verbose_name=_("Attribute Name"),
        help_text=_("The name of the attribute, e.g., 'Color', 'Size'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Attribute Slug"),
        help_text=_("A unique, URL-friendly version of the name.")
    )
    attribute_type = models.CharField(
        max_length=20,
        choices=AttributeTypeChoices.choices,
        default=AttributeTypeChoices.TEXT,
        verbose_name=_("Data Type"),
        help_text=_("Determines the data type of the attribute's values (e.g., text, number).")
    )
    display_type = models.CharField(
        max_length=50,
        choices=DisplayTypeChoices.choices,
        default=DisplayTypeChoices.DROPDOWN,
        verbose_name=_("Display Type"),
        help_text=_("How this attribute should be displayed on the product page.")
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_("Unit of Measurement"),
        help_text=_("The unit for this attribute, if applicable (e.g., 'kg', 'cm', 'GB').")
    )
    help_text = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Help Text"),
        help_text=_("Additional instructions or information for this attribute shown to the user.")
    )
    is_variant_defining = models.BooleanField(
        default=False,
        verbose_name=_("Is Variant Defining"),
        help_text=_("If true, this attribute is used to create product variants (e.g., color, size).")
    )
    is_filterable = models.BooleanField(
        default=False,
        verbose_name=_("Is Filterable"),
        help_text=_("If true, this attribute can be used for filtering products.")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
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
        verbose_name=_("Attribute"),
        help_text=_("The attribute this value belongs to, e.g., 'Color', 'Size'.")
    )
    value = models.CharField(
        max_length=255,
        verbose_name=_("Value"),
        help_text=_("the actual value, e.g., 'Red', 'XL', '256GB'.")
    )
    slug = models.SlugField(
        max_length=255,
        allow_unicode=True,
        verbose_name=_("Value Slug"),
        help_text=_("A unique, URL-friendly version of the value.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )
    meta = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_("Meta Data"),
        help_text=_("Extra data, e.g., {'hex_code': '#FF0000'} for a color.")
    )

    class Meta:
        verbose_name = _("Attribute Value")
        verbose_name_plural = _("Attribute Values")
        ordering = ['display_order', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['attribute', 'value'],
                name='unique_value_per_attribute'
            ),
            models.UniqueConstraint(
                fields=['attribute', 'slug'],
                name='unique_slug_per_attribute'
            )
        ]

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductType(MPTTModel, TimeStampedModel):
    """
    Defines a "blueprint" for a product, grouping a set of attributes.
    e.g., A "T-Shirt" product type, can be hierarchical.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Type Name"),
        help_text=_("A name for the product type, e.g., 'T-Shirt', 'Smartphone'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Product Type Slug"),
        help_text=_("A unique, URL-friendly version of the product type name.")
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        verbose_name=_("Parent Product Type"),
        help_text=_("The parent type for hierarchical grouping. e.g., 'Apparel'.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of the product type.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )
    attributes = models.ManyToManyField(
        "Attribute",
        through='ProductTypeAttribute',
        blank=True,
        verbose_name=_("Attributes"),
        help_text=_("Attributes associated with this product type.")
    )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("Product Type")
        verbose_name_plural = _("Product Types")
        ordering = ['display_order', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'parent'],
                name='unique_product_type_name_in_parent'
            ),
            models.UniqueConstraint(
                fields=['slug', 'parent'],
                name='unique_product_type_slug_in_parent'
            )
        ]

    def __str__(self):
        return self.name


class ProductTypeAttribute(TimeStampedModel):
    """Through model to store metadata about the relationship between a ProductType and an Attribute."""
    product_type = models.ForeignKey(
        "ProductType",
        on_delete=models.CASCADE,
        verbose_name=_("Product Type"),
        help_text=_("The product type this attribute belongs to, e.g., 'T-Shirt', 'Smartphone'.")
    )
    attribute = models.ForeignKey(
        "Attribute",
        on_delete=models.CASCADE,
        verbose_name=_("Attribute"),
        help_text=_("The attribute associated with this product type, e.g., 'Color', 'Size'.")
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Is Required"),
        help_text=_("Indicates if this attribute is required for products of this type.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )

    class Meta:
        verbose_name = _("Product Type Attribute")
        verbose_name_plural = _("Product Type Attributes")
        ordering = ['display_order', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['product_type', 'attribute'],
                name='unique_attribute_per_product_type'
            )
        ]

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
        verbose_name=_("Product Type"),
        help_text=_("The type of the product, which defines its attributes.")
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_("Product Name"),
        help_text=_("The main name of the product.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Product Slug"),
        help_text=_("A unique, URL-friendly version of the product name.")
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Short Description"),
        help_text=_("A brief description of the product, suitable for listings or search results.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A detailed description of the product, suitable for the product page.")
    )
    brand = models.ForeignKey(
        "Brand",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name=_("Brand"),
        help_text=_("The brand or manufacturer of the product, if any.")
    )
    categories = TreeManyToManyField(
        "Category",
        blank=True,
        related_name='products',
        verbose_name=_("Categories"),
        help_text=_("The categories this product belongs to.")
    )
    tags = models.ManyToManyField(
        "Tag",
        blank=True,
        related_name='products',
        verbose_name=_("Tags"),
        help_text=_("Tags associated with this product for grouping or filtering.")
    )
    media_links = GenericRelation(
        'media.MediaLink',
        verbose_name=_("Media Links"),
        help_text=_("Links to media files (images, videos) associated with this product.")
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        verbose_name=_("Published At"),
        help_text=_("Set a future date to schedule publication. If blank, it publishes immediately when activated. (Optional)")
    )
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'brand'],
                name='unique_product_name_per_brand'
            )
        ]

    def __str__(self):
        return self.name

    @cached_property
    def default_variant(self):
        """Returns the default variant for the product."""
        return self.variants.filter(is_active=True, is_default=True).first()

    @cached_property
    def featured_image(self):
        """Returns the featured image for the product."""
        featured_link = self.media_links.filter(is_featured=True).first()
        if featured_link and featured_link.media.media_type == Media.MediaTypeChoices.IMAGE:
            return featured_link.media
        return None


class ProductVariant(TimeStampedModel):
    """
    Represents a specific, sellable version of a Product.
    e.g., "Apple iPhone 15 Pro - 256GB - Blue"
    """
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_("Product"),
        help_text=_("The parent product this variant belongs to.")
    )
    name = models.CharField(
        max_length=255,
        blank=True,  # Can be auto-generated
        verbose_name=_("Variant Name"),
        help_text=_("A specific name for this variant, e.g., 'Large, Red'. Can be auto-generated.")
    )
    sku = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("SKU (Stock Keeping Unit)"),
        help_text=_("The unique identifier for this variant, used for inventory management.")
    )
    upc = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("UPC (Universal Product Code)"),
        help_text=_("The barcode number for this variant.")
    )
    unit = models.CharField(
        max_length=50,
        default=_("Item"),
        verbose_name=_("Unit of Sale"),
        help_text=_("The unit in which this variant is sold, e.g., 'kg', 'bottle', 'pack'.")
    )
    attributes = models.ManyToManyField(
        "AttributeValue",
        verbose_name=_("Attributes"),
        help_text=_("The specific attribute values that define this variant (e.g., Color: Red, Size: Large).")
    )
    media_links = GenericRelation(
        'media.MediaLink',
        verbose_name=_("Media Links"),
        help_text=_("Links to media files (images, videos) specific to this variant.")
    )
    max_order_quantity = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Maximum Order Quantity"),
        help_text=_("the maximum quantity a customer can purchase in a single order. If blank, the stock quantity is the limit.")
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("Is Default"),
        help_text=_("If true, this variant is shown by default on the product page.")
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
    )

    objects = ProductVariantQuerySet.as_manager()

    class Meta:
        verbose_name = _("Product Variant")
        verbose_name_plural = _("Product Variants")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} - {self.name or self.sku}"

    def save(self, *args, **kwargs):
        if not self.name:
            # Auto-generate a name if it's blank
            self.name = self.sku
        super().save(*args, **kwargs)


class ProductCollection(TimeStampedModel):
    """
    Represents a collection of products, which can be used for marketing or organization.
    e.g., "Summer Sale", "Homepage Featured", "Staff Picks"
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Collection Name"),
        help_text=_("The name of the collection, e.g., 'Summer Sale', 'Homepage Featured'.")
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Collection Slug"),
        help_text=_("A unique, URL-friendly version of the collection name.")
    )
    products = models.ManyToManyField(
        Product,
        through='ProductCollectionEntry',
        related_name='collections',
        blank=True,
        verbose_name=_("Products"),
        help_text=_("The products included in this collection.")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("A brief description of the collection, suitable for marketing or informational purposes.")
    )
    image = models.FileField(
        upload_to=GenerateUploadPath(base_path='uploads/collections/'),
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
        verbose_name=_("Start Date"),
        help_text=_("The date and time when the collection becomes active.")
    )
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("End Date"),
        help_text=_("The date and time when the collection expires.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )
    is_active = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Is Active"),
        help_text=_("Controls active status. Inactive items are hidden without being deleted.")
    )

    class Meta:
        verbose_name = _("Product Collection")
        verbose_name_plural = _("Product Collections")
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.name


class ProductCollectionEntry(TimeStampedModel):
    """Through model to associate products with collections."""
    collection = models.ForeignKey(
        "ProductCollection",
        on_delete=models.CASCADE,
        verbose_name=_("Product Collection"),
        help_text=_("The collection this entry belongs to.")
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_("Product"),
        help_text=_("The product that is part of this collection entry.")
    )
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order"),
        help_text=_("The order in which this item appears in the list. Lower numbers appear first.")
    )

    class Meta:
        verbose_name = _("Product Collection Entry")
        verbose_name_plural = _("Product Collection Entries")
        ordering = ['display_order', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['collection', 'product'],
                name='unique_product_per_collection'
            )
        ]


class Price(TimeStampedModel):
    """Represents the pricing information for a specific ProductVariant."""
    variant = models.ForeignKey(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name='prices',
        verbose_name=_("Product Variant"),
        help_text=_("The product variant this price applies to.")
    )
    currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        related_name='prices',
        verbose_name=_("Currency"),
        help_text=_("The currency in which the price is set, e.g., USD, EUR.")
    )
    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name=_("Base Price"),
        help_text=_("The standard price of the variant without any discounts or sales.")
    )
    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name=_("Sale Price"),
        help_text=_("The discounted price during a sale. If not set, the base price is used.")
    )
    sale_start_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Sale Start Date"),
        help_text=_("The date and time when the sale price becomes active. If blank, the sale starts immediately.")
    )
    sale_end_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Sale End Date"),
        help_text=_("The date and time when the sale price expires. If blank, the sale does not expire automatically.")
    )
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        verbose_name=_("Cost Price"),
        help_text=_("The cost price of the variant, used for profit calculations. If not set, profit cannot be calculated.")
    )

    class Meta:
        verbose_name = _("Price")
        verbose_name_plural = _("Prices")
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['variant', 'currency'],
                name='unique_price_per_variant_currency'
            )
        ]

    def __str__(self):
        return f"{self.variant} - {self.base_price} {self.currency.code}"

    @property
    def is_on_sale(self):
        """Checks if the sale price is currently active."""
        from django.utils import timezone

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
    """Represents the stock and inventory information for a specific ProductVariant."""
    variant = models.OneToOneField(
        "ProductVariant",
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name=_("Product Variant"),
        help_text=_("The product variant this inventory applies to.")
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Quantity"),
        help_text=_("The actual number of items in stock.")
    )
    threshold = models.PositiveIntegerField(
        default=10,
        verbose_name=_("Low Stock Threshold"),
        help_text=_("When available stock reaches this level, a notification can be triggered.")
    )
    track_inventory = models.BooleanField(
        default=True,
        verbose_name=_("Track Inventory"),
        help_text=_("If false, stock levels will not be tracked for this variant.")
    )
    allow_backorders = models.BooleanField(
        default=False,
        verbose_name=_("Allow Backorders"),
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
        return self.quantity

    @property
    def is_in_stock(self):
        """Checks if the variant is currently in stock."""
        if not self.track_inventory:
            return True
        return self.available_quantity > 0

    @property
    def is_low_stock(self):
        """Checks if the variant is below the low stock threshold."""
        if not self.track_inventory:
            return False
        return self.available_quantity <= self.threshold
