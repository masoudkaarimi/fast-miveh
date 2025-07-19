from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.account.permissions import IsOwnerOrReadOnly
from apps.account.serializers import (
    EmailAddSerializer,
    RequestOTPSerializer,
    EmailVerifySerializer,
    PasswordSetSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer,
    LoginWithPasswordSerializer,
    VerifyOTPAndLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    IdentifierStatusCheckSerializer,
    PasswordResetConfirmWithOTPSerializer,
)

User = get_user_model()


class IdentifierStatusCheckView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = IdentifierStatusCheckSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RequestOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        return Response(serializer.data, status=status.HTTP_200_OK)
        # return Response({"detail": _("The password has been set successfully.")}, status=status.HTTP_200_OK)


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
        return Response(serializer.data, status=status.HTTP_200_OK)


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
