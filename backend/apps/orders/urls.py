from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.orders import views

app_name = 'orders'

router = DefaultRouter()
# router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    # --- Cart Management ---
    path('cart/', views.CartViewSet.as_view({'get': 'list', 'post': 'create'}), name='cart_list_create'),
    path('cart/clear/', views.CartViewSet.as_view({'post': 'clear'}), name='cart_clear'),
    path('cart/items/<int:item_pk>/', views.CartViewSet.as_view({'patch': 'update_item', 'delete': 'remove_item'}), name='cart_item_update_remove'),

    # --- Checkout ---
    path('checkout/', views.CheckoutAPIView.as_view(), name='checkout'),

    # --- Order Management ---
    path('', include(router.urls)),
]
