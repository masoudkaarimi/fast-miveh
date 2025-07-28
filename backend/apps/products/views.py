from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.products.filters import ProductFilter
from apps.products.services import ProductService
from apps.products.exceptions import ProductNotFound
from apps.products.models import Product, Category, Brand, Tag, ProductCollection
from apps.products.serializers import (
    ProductListSerializer, ProductDetailSerializer, CategorySerializer, BrandSerializer,
    TagSerializer, ProductCollectionDetailSerializer, ProductCollectionSerializer,
)


class ProductListView(generics.ListAPIView):
    """
    API view to list all published products. Supports advanced filtering and ordering.
    e.g., /api/products/?category_slug=laptops&brand_slug=apple
    """
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filterset_class = ProductFilter

    def get_queryset(self):
        """
        Return the queryset for the product list, ensuring no duplicates
        are returned when filtering across multiple related tables.
        """
        return Product.objects.published().with_details().distinct()


class ProductDetailView(generics.GenericAPIView):
    """API view to retrieve the detailed information for a single product."""
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer

    def get(self, request, slug: str, *args, **kwargs):
        """Handles GET request for a single product by its slug."""
        try:
            service = ProductService(product_slug=slug)
            product_context = service.get_context_for_detail_page()
            serializer = self.get_serializer(product_context)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class CategoryListView(generics.ListAPIView):
    """API view to list all active categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    """API view to retrieve a single category by its slug."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class BrandListView(generics.ListAPIView):
    """API view to list all active brands."""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]


class BrandDetailView(generics.RetrieveAPIView):
    """API view to retrieve a single brand by its slug."""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class TagListView(generics.ListAPIView):
    """API view to list all active tags."""
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer
    permission_classes = [AllowAny]


class TagDetailView(generics.RetrieveAPIView):
    """API view to retrieve a single tag by its slug."""
    queryset = Tag.objects.filter(is_active=True)
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class ProductCollectionListView(generics.ListAPIView):
    serializer_class = ProductCollectionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Returns collections that are active and currently within their
        start and end dates (if specified).
        """
        now = timezone.now()
        return ProductCollection.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(Q(end_date__gte=now) | Q(end_date__isnull=True))


class ProductCollectionDetailView(generics.RetrieveAPIView):
    """API view to retrieve a single product collection by its slug."""
    queryset = ProductCollection.objects.filter(is_active=True)
    serializer_class = ProductCollectionDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
