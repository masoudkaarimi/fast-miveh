from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.payments import views

app_name = 'payments'

router = DefaultRouter()
router.register(r'transactions', views.PaymentTransactionViewSet, basename='transaction')

urlpatterns = [
    # --- Payment Gateway List ---
    path('payments/gateways/', views.PaymentGatewayListView.as_view(), name='gateway_list'),

    # --- Payment Transaction Creation & Verification ---
    path('payments/transactions/create/', views.PaymentTransactionCreateView.as_view(), name='transaction_create'),
    path('payments/transactions/verify/', views.PaymentTransactionVerifyView.as_view(), name='transaction_verify'),

    # --- Transaction Management ---
    path('payments/', include(router.urls)),
]
