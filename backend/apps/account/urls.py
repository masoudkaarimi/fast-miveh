from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.account import views

app_name = 'account'

router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, basename='address')

urlpatterns = [
    # --- Login/Registration ---
    path('auth/status/', views.IdentifierStatusCheckView.as_view(), name='auth_status_check'),
    path('auth/otp/request/', views.RequestOTPView.as_view(), name='auth_otp_request'),
    path('auth/otp/verify/', views.VerifyOTPAndLoginView.as_view(), name='auth_otp_verify'),
    path('auth/login/', views.LoginWithPasswordView.as_view(), name='auth_login_password'),

    # --- Token Management ---
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- User Profile & Account Management (Authenticated) ---
    path('profile/me/', views.UserProfileView.as_view(), name='profile_me'),
    path('profile/set-password/', views.PasswordSetView.as_view(), name='profile_set_password'),
    path('profile/change-password/', views.PasswordChangeView.as_view(), name='profile_change_password'),
    path('profile/email/add/', views.EmailAddView.as_view(), name='profile_email_add'),
    path('profile/email/verify/', views.EmailVerifyView.as_view(), name='profile_email_verify'),

    # --- Wishlist and Address Management ---
    path('profile/wishlist/', views.WishlistAPIView.as_view(), name='wishlist_api'),
    path('profile/', include(router.urls)),

    # --- Standalone Password Reset Flow (Unauthenticated) ---
    path('password-reset/request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm_link'),
    path('password-reset/confirm-otp/', views.PasswordResetConfirmWithOTPView.as_view(), name='password_reset_confirm_otp'),
]
