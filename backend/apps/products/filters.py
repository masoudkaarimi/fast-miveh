import django_filters
from django.db.models import Q
from django.utils import timezone

from apps.products.models import Attribute, Category, Product


class ProductFilter(django_filters.FilterSet):
    """
    An advanced and dynamic filter set for the Product model.

    Supports filtering by static fields like category and brand, as well as
    dynamically generated filters for any 'filterable' attributes.
    Also includes sorting and full-text search capabilities.
    """

    # --- Static Filters ---

    # Full-text search on name, description, and brand name
    search = django_filters.CharFilter(method='filter_by_all_name_fields', label="Search")

    # Filter by category slug, including all its descendant categories
    category = django_filters.CharFilter(method='filter_by_category', label="Category Slug")

    # Filter by brand slug
    brand = django_filters.CharFilter(field_name='brand__slug', lookup_expr='iexact')

    # Filter by multiple tag slugs, comma-separated (e.g., ?tags=new,featured)
    tags = django_filters.AllValuesMultipleFilter(field_name='tags__slug', lookup_expr='iexact')

    # Price range filter
    min_price = django_filters.NumberFilter(field_name="variants__prices__base_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="variants__prices__base_price", lookup_expr='lte')

    # Boolean filter for products on sale
    on_sale = django_filters.BooleanFilter(method='filter_on_sale')

    # --- Ordering Filter ---

    # Allow sorting on different fields (e.g., ?ordering=name, ?ordering=-created_at)
    ordering = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('created_at', 'created_at'),
            ('variants__prices__base_price', 'price'),
        ),
        label="Ordering"
    )

    class Meta:
        model = Product
        fields = ['search', 'category', 'brand', 'tags', 'min_price', 'max_price', 'on_sale']

    def __init__(self, *args, **kwargs):
        """Dynamically adds filters for all 'filterable' attributes."""
        super().__init__(*args, **kwargs)

        filterable_attributes = Attribute.objects.filter(is_filterable=True, is_active=True)

        for attr in filterable_attributes:
            self.filters[attr.slug] = django_filters.CharFilter(method='filter_by_dynamic_attribute', label=attr.name)

    # --- Custom Filter Methods ---

    @staticmethod
    def filter_by_all_name_fields(queryset, name, value):
        """Perform a case-insensitive search across multiple text fields."""
        if not value:
            return queryset

        return queryset.filter(
            Q(name__icontains=value) |
            Q(slug__icontains=value) |
            Q(description__icontains=value) |
            Q(brand__name__icontains=value)
        )

    @staticmethod
    def filter_by_category(queryset, name, value):
        """Filter by a category slug and all of its descendants."""
        try:
            if not value:
                return queryset

            category = Category.objects.get(slug=value)
            categories = category.get_descendants(include_self=True)
            return queryset.filter(categories__in=categories)
        except Category.DoesNotExist:
            return queryset.none()

    @staticmethod
    def filter_on_sale(queryset, name, value):
        """Filters products that have at least one variant with a currently active sale."""
        if not value:
            return queryset

        now = timezone.now()

        sale_price_exists = Q(variants__prices__sale_price__isnull=False)
        sale_has_started = Q(variants__prices__sale_start_date__isnull=True) | Q(variants__prices__sale_start_date__lte=now)
        sale_has_not_ended = Q(variants__prices__sale_end_date__isnull=True) | Q(variants__prices__sale_end_date__gte=now)

        return queryset.filter(sale_price_exists & sale_has_started & sale_has_not_ended).distinct()

    @staticmethod
    def filter_by_dynamic_attribute(queryset, name, value):
        """
        The method that handles filtering for all dynamically created attribute filters.
        It filters products that have a variant matching the given attribute slug and value.
        e.g., name='color', value='red' -> filters for variants with Attribute 'color' and Value 'red'.
        """
        if not value:
            return queryset

        return queryset.filter(
            variants__attributes__attribute__slug=name,
            variants__attributes__value__iexact=value
        )
