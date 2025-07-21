from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from apps.products.services import ProductService
from apps.products.exceptions import ProductNotFound
from apps.products.models import Product, Category, Brand, Tag, ProductCollection
from apps.products.serializers import (ProductListSerializer, ProductDetailSerializer, CategorySerializer, BrandSerializer, TagSerializer, )


# --- Product Views ---
class ProductListView(generics.ListAPIView):
    """
    API view to list all published products. Supports filtering.
    e.g., /api/products/?category_slug=laptops&brand_slug=apple
    """
    queryset = Product.objects.published().with_details()
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    # NOTE: Filtering logic will be added later using a filter backend.


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


# --- Category Views ---
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


# --- Brand Views ---
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


# --- Tag Views ---
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

