from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from mptt.admin import DraggableMPTTAdmin

from apps.media.admin import MediaLinkInline
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
    ProductCollectionEntry,
    ProductType,
    ProductTypeAttribute,
    ProductVariant,
    Tag,
)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('display_logo', 'name', 'slug', 'is_active', 'display_order')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def display_logo(self, obj):
        if obj.logo and obj.logo.url:
            return format_html('<img src="{}" width="25" height="25" />', obj.logo.url)
        return "N/A"

    display_logo.short_description = 'Logo'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'display_image', 'slug', 'is_active')
    list_display_links = ('indented_title',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

    def display_image(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" width="25" height="25" />', obj.image.url)
        return "N/A"

    display_image.short_description = 'Image'


class AttributeValueInline(admin.TabularInline):
    model = AttributeValue
    extra = 1
    prepopulated_fields = {'slug': ('value',)}


@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'unit', 'attribute_type', 'is_variant_defining', 'is_filterable', 'is_active')
    list_filter = ('attribute_type', 'is_variant_defining', 'is_filterable', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [AttributeValueInline]


class ProductTypeAttributeInline(admin.TabularInline):
    model = ProductTypeAttribute
    extra = 1
    raw_id_fields = ('attribute',)


@admin.register(ProductType)
class ProductTypeAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'slug', 'display_order')
    list_display_links = ('indented_title',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductTypeAttributeInline]


class PriceInline(admin.TabularInline):
    model = Price
    extra = 1
    can_delete = False


class InventoryInline(admin.StackedInline):
    model = Inventory
    can_delete = False


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'sku', 'unit', 'max_order_quantity', 'is_active', 'is_default')
    list_filter = ('is_active', 'is_default')
    search_fields = ('name', 'sku', 'product__name')
    raw_id_fields = ('product',)
    inlines = [PriceInline, InventoryInline, MediaLinkInline]
    filter_horizontal = ('attributes',)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ('name', 'sku', 'unit', 'max_order_quantity', 'is_active', 'is_default')
    readonly_fields = ('name',)
    show_change_link = True


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'brand', 'product_type', 'is_active', 'published_at')
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
    inlines = [ProductCollectionEntryInline]
    list_display = ('display_image', 'name', 'slug', 'is_active', 'start_date', 'end_date')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def display_image(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" width="25" height="25" />', obj.image.url)
        return "N/A"

    display_image.short_description = 'Image'


@admin.register(BackInStockSubscription)
class BackInStockSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('variant', 'display_recipient', 'status', 'created_at',)
    list_filter = ('status', 'created_at',)
    search_fields = ('variant__name', 'variant__sku', 'user__username', 'user__email', 'email',)
    readonly_fields = ('user', 'email', 'variant', 'created_at', 'updated_at',)
    raw_id_fields = ('user', 'variant')
    ordering = ('-created_at',)
    actions = ['mark_as_pending']

    def has_add_permission(self, request):
        """Disables the "Add" button"""
        return False

    # def has_change_permission(self, request, obj=None):
    #     """Disables the "Save" and "Save and continue editing" buttons"""
    #     return False

    def has_delete_permission(self, request, obj=None):
        """Disables the "Delete" action"""
        return False

    @admin.display(description=_('Recipient'))
    def display_recipient(self, obj):
        if obj.user:
            return obj.user.get_username()
        return obj.email

    display_recipient.short_description = 'Recipient'

    @admin.action(description=_('Mark selected subscriptions as Pending'))
    def mark_as_pending(self, request, queryset):
        queryset.update(status=BackInStockSubscription.StatusChoices.PENDING)
        self.message_user(request, _('Selected subscriptions have been marked as Pending.'))
