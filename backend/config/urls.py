from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

api_urlpatterns = [
    re_path(r'^(?P<version>v\d+)/', include('apps.core.urls', namespace='configuration')),
    re_path(r'^(?P<version>v\d+)/', include('apps.account.urls', namespace='account')),
    re_path(r'^(?P<version>v\d+)/', include('apps.products.urls', namespace='products')),
    re_path(r'^(?P<version>v\d+)/', include('apps.orders.urls', namespace='orders')),
    re_path(r'^(?P<version>v\d+)/', include('apps.payments.urls', namespace='payments')),
    re_path(r'^(?P<version>v\d+)/', include('apps.wallets.urls', namespace='wallets')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns = [
    # Group all API urls under a single path
    path('api/', include(api_urlpatterns)),
]

# urlpatterns += i18n_patterns(
urlpatterns += [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]
# )

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r'^rosetta/', include('rosetta.urls'))]

# Static and media files serving during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
