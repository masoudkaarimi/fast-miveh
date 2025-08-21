from django.db import models
from django.utils import timezone


class ProductQuerySet(models.QuerySet):
    """QuerySet for the Product model to encapsulate common queries."""

    def published(self):
        """Returns only active products that are available for viewing."""
        now = timezone.now()
        return self.filter(is_active=True, published_at__lte=now)

    def with_details(self):
        """Optimizes product retrieval by prefetching related data needed for list or detail pages."""
        return self.select_related(
            'brand', 'product_type'  # ForeignKey or OneToOneField
        ).prefetch_related(
            'categories',  # ManyToManyField
            'tags',
            'variants__prices',
            'variants__inventory',
            'media_links__media'
        )


class ProductVariantQuerySet(models.QuerySet):
    """QuerySet for the ProductVariant model."""

    def active(self):
        """Returns only active variants belonging to published products."""
        from apps.products.models import Product

        published_products = Product.objects.published()
        return self.filter(is_active=True, product__in=published_products)
