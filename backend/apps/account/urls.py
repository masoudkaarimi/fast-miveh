from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.account.views import (
    EmailAddView,
    RequestOTPView,
    UserProfileView,
    PasswordSetView,
    EmailVerifyView,
    PasswordChangeView,
    VerifyOTPAndLoginView,
    LoginWithPasswordView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    IdentifierStatusCheckView,
    PasswordResetConfirmWithOTPView,
    AddressViewSet
)

app_name = 'account'

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='address')

urlpatterns = [
    # --- Login/Registration ---
    path('auth/status/', IdentifierStatusCheckView.as_view(), name='auth_status_check'),
    path('auth/otp/request/', RequestOTPView.as_view(), name='auth_otp_request'),
    path('auth/otp/verify/', VerifyOTPAndLoginView.as_view(), name='auth_otp_verify'),
    path('auth/login/', LoginWithPasswordView.as_view(), name='auth_login_password'),

    # --- Token Management ---
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- User Profile & Account Management (Authenticated) ---
    path('profile/me/', UserProfileView.as_view(), name='profile_me'),
    path('profile/set-password/', PasswordSetView.as_view(), name='profile_set_password'),
    path('profile/change-password/', PasswordChangeView.as_view(), name='profile_change_password'),
    path('profile/email/add/', EmailAddView.as_view(), name='profile_email_add'),
    path('profile/email/verify/', EmailVerifyView.as_view(), name='profile_email_verify'),

    # --- Standalone Password Reset Flow (Unauthenticated) ---
    path('password-reset/request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm_link'),
    path('password-reset/confirm-otp/', PasswordResetConfirmWithOTPView.as_view(), name='password_reset_confirm_otp'),

    # --- Wishlist and Address Management (New additions) ---
    # path('wishlist/', WishlistAPIView.as_view(), name='wishlist'),

    # --- Address Management ---
    path('', include(router.urls)),
]
