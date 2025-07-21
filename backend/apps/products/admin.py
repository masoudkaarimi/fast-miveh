from django.contrib import admin

from mptt.admin import DraggableMPTTAdmin

from apps.products.models import (
    Currency, Category, Brand, Tag, Attribute, AttributeValue, ProductType, ProductTypeAttribute, Product, ProductVariant, ProductCollection,
    ProductCollectionEntry, Price, Inventory
)
from apps.media.admin import MediaLinkInline


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'symbol', 'exchange_rate', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')
    search_fields = ('code', 'name')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'slug', 'is_active')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    prepopulated_fields = {'slug': ('value',)}


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'attribute_type', 'is_variant_defining', 'is_filterable', 'is_active')
    list_filter = ('attribute_type', 'is_variant_defining', 'is_filterable', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttributeValueInline]


class ProductTypeAttributeInline(admin.TabularInline):
    model = ProductTypeAttribute
    extra = 1
    raw_id_fields = ('attribute',)


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'display_order')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductTypeAttributeInline]


class PriceInline(admin.TabularInline):
    model = Price
    extra = 1


class InventoryInline(admin.StackedInline):
    model = Inventory
    can_delete = False


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'sku', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'sku', 'product__name')
    raw_id_fields = ('product', 'attributes')
    inlines = [PriceInline, InventoryInline]


class ProductVariantInline(admin.TabularInline):
    """A compact inline for showing variants on the Product admin page."""
    model = ProductVariant
    extra = 0
    fields = ('name', 'sku', 'is_active', 'is_default')
    readonly_fields = ('name',)
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'product_type', 'is_active', 'published_at')
    list_filter = ('is_active', 'brand', 'product_type', 'categories')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ('categories', 'tags')
    raw_id_fields = ('brand', 'product_type')
    inlines = [ProductVariantInline, MediaLinkInline]
    fieldsets = (
        ('Core Information', {'fields': ('name', 'slug', 'product_type', 'brand')}),
        ('Content', {'fields': ('short_description', 'description')}),
        ('Categorization', {'fields': ('categories', 'tags')}),
        ('Status', {'fields': ('is_active', "published_at")}),
    )


class ProductCollectionEntryInline(admin.TabularInline):
    model = ProductCollectionEntry
    extra = 1
    raw_id_fields = ('product',)


@admin.register(ProductCollection)
class ProductCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductCollectionEntryInline]
