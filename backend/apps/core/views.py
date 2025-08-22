from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.core.models import SiteConfiguration
from apps.core.serializers import SiteConfigurationSerializer


class SiteConfigurationAPIView(generics.RetrieveAPIView):
    """Provides a public, read-only endpoint to fetch site-wide configuration."""
    permission_classes = [AllowAny]
    serializer_class = SiteConfigurationSerializer

    def get_object(self):
        return SiteConfiguration.get_solo()
