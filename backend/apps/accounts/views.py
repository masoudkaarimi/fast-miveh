from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import Address, Wishlist
from apps.accounts.permissions import IsOwnerOrReadOnly
from apps.accounts.serializers import (
    AddressSerializer,
    EmailAddSerializer,
    EmailVerifySerializer,
    IdentifierStatusCheckSerializer,
    LoginWithPasswordSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetConfirmWithOTPSerializer,
    PasswordResetRequestSerializer,
    PasswordSetSerializer,
    RequestOTPSerializer,
    UserProfileSerializer,
    VerifyOTPAndLoginSerializer,
    WishlistActionSerializer,
    WishlistSerializer,
)

User = get_user_model()


class IdentifierStatusCheckView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdentifierStatusCheckSerializer
    throttle_scope = 'identifier_status_check'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RequestOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestOTPSerializer
    throttle_scope = 'request_otp'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class VerifyOTPAndLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPAndLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class LoginWithPasswordView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginWithPasswordSerializer
    throttle_scope = 'login_with_password'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related('profile').all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        return self.request.user


class PasswordSetView(generics.GenericAPIView):
    """Allows a user who registered via OTP to set their password for the first time."""
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordSetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("The password has been set successfully.")}, status=status.HTTP_200_OK)


class PasswordChangeView(generics.GenericAPIView):
    """Allows an authenticated user to change their existing password."""
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("The password has been changed successfully.")}, status=status.HTTP_200_OK)


class EmailAddView(generics.GenericAPIView):
    """Adds or changes a user's email and sends a verification OTP."""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailAddSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class EmailVerifyView(generics.GenericAPIView):
    """Verifies the user's email address with an OTP."""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("The email address has been verified successfully.")}, status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.GenericAPIView):
    """Initiates the password reset process via email or phone."""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Return a generic message to prevent user enumeration
        return Response({"detail": _("If an account with that identifier exists and is verified, password reset instructions have been sent.")}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(generics.GenericAPIView):
    """Finalizes password reset using the token from the email link."""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("The password has been reset successfully.")}, status=status.HTTP_200_OK)


class PasswordResetConfirmWithOTPView(generics.GenericAPIView):
    """Finalizes password reset using an OTP code from SMS."""
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmWithOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": _("The password has been reset successfully.")}, status=status.HTTP_200_OK)


class AddressViewSet(viewsets.ModelViewSet):
    """A viewset for managing user addresses."""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """This view should return a list of all addresses for the currently authenticated user. Excludes snapshots."""
        return Address.objects.filter(user=self.request.user, is_snapshot=False)

    def perform_create(self, serializer):
        """Assign the current user to the address when creating it."""
        serializer.save(user=self.request.user)


# # TODO: Check it
class WishlistAPIView(generics.GenericAPIView):
    """
    A single API view to manage the user's wishlist.
    - GET: Retrieve the full wishlist.
    - POST: Add a variant to the wishlist.
    - DELETE: Remove a variant from the wishlist.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return the appropriate serializer class based on the request method.
        """
        if self.request.method == 'GET':
            return WishlistSerializer
        # For both POST (add) and DELETE (remove), we validate the variant_id
        return WishlistActionSerializer

    def get_object(self):
        """Get or create a wishlist for the current user."""
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist

    def get(self, request, *args, **kwargs):
        """Handle GET request to retrieve the wishlist."""
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """Handle POST request to add a variant to the wishlist."""
        wishlist = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant_id = serializer.validated_data['variant_id']

        wishlist.variants.add(variant_id)

        return Response({"detail": "Variant added to wishlist successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """Handle DELETE request to remove a variant from the wishlist."""
        wishlist = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        variant_id = serializer.validated_data['variant_id']

        wishlist.variants.remove(variant_id)

        return Response(status=status.HTTP_204_NO_CONTENT)
