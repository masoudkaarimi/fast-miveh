from django.urls import path

from apps.core.views import SiteConfigurationAPIView

app_name = 'configuration'

urlpatterns = [
    path('site-config/', SiteConfigurationAPIView.as_view(), name='site_config'),
]
