from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.products.exceptions import ProductNotFound
from apps.products.filters import ProductFilter
from apps.products.models import Brand, Category, Product, ProductCollection
from apps.products.serializers import (
    BackInStockSubscriptionSerializer,
    BrandSerializer,
    CategorySerializer,
    ProductCollectionDetailSerializer,
    ProductCollectionSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
)
from apps.products.services import ProductService


class BrandListView(generics.ListAPIView):
    """API view to list all brands."""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]


class BrandDetailView(generics.RetrieveAPIView):
    """API view to retrieve a single brand by its slug."""
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class CategoryListView(generics.ListAPIView):
    """API view to list all categories."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    """API view to retrieve a single category by its slug."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class ProductListView(generics.ListAPIView):
    """API view to list all products with filtering and pagination."""
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]
    filterset_class = ProductFilter

    def get_queryset(self):
        return Product.objects.published().with_details().distinct()


class ProductDetailView(generics.GenericAPIView):
    """API view to retrieve a single product by its slug."""
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer

    def get(self, request, slug, *args, **kwargs):
        try:
            service = ProductService(product_slug=slug, request=request)
            product_context = service.get_context_for_detail_page()
            serializer = self.get_serializer(product_context)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ProductNotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class ProductCollectionListView(generics.ListAPIView):
    """API view to list all active product collections."""
    serializer_class = ProductCollectionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Returns a queryset of active product collections that are currently valid."""
        now = timezone.now()
        return ProductCollection.objects.filter(is_active=True, start_date__lte=now).filter(Q(end_date__gte=now) | Q(end_date__isnull=True))


class ProductCollectionDetailView(generics.RetrieveAPIView):
    """API view to retrieve a single product collection by its slug."""
    queryset = ProductCollection.objects.filter(is_active=True)
    serializer_class = ProductCollectionDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class BackInStockSubscriptionView(APIView):
    """API view to handle back-in-stock subscriptions for product variants."""
    permission_classes = [AllowAny]
    serializer_class = BackInStockSubscriptionSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs.setdefault('context', {'request': self.request})
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": _("You will be notified when this product is back in stock.")}, status=status.HTTP_201_CREATED)
