from django.urls import path

from apps.products import views

app_name = 'products'

urlpatterns = [
    # --- Product ---
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),

    # --- Category ---
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/<slug:slug>/", views.CategoryDetailView.as_view(), name="category_detail"),

    # --- Brand ---
    path("brands/", views.BrandListView.as_view(), name="brand_list"),
    path("brands/<slug:slug>/", views.BrandDetailView.as_view(), name="brand_detail"),

    # --- Tag ---
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tags/<slug:slug>/", views.TagDetailView.as_view(), name="tag_detail"),

    # --- Product Collection ---
    path("collections/", views.ProductCollectionListView.as_view(), name="collection_list"),
    path("collections/<slug:slug>/", views.ProductCollectionDetailView.as_view(), name="collection_detail"),
]
