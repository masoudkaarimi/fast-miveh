from django.db import models
from django.utils import timezone


class ProductQuerySet(models.QuerySet):
    """Custom QuerySet for the Product model to encapsulate common queries."""

    def published(self):
        """
        Returns only active products that are available for viewing.
        - is_active is True
        - published_at is not in the future
        """
        now = timezone.now()
        return self.filter(is_active=True, published_at__lte=now)

    def with_details(self):
        """
        Optimizes product retrieval by prefetching related data
        needed for list or detail pages.
        """
        return self.select_related(
            'category', 'brand', 'product_type'
        ).prefetch_related(
            'variants__prices', 'variants__inventory', 'media'
        )


class ProductVariantQuerySet(models.QuerySet):
    """Custom QuerySet for the ProductVariant model."""

    def active(self):
        """Returns only active variants belonging to published products."""
        return self.filter(is_active=True, product__is_active=True)
