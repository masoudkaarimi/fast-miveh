from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),

    re_path(r'^api/(?P<version>v\d+)/', include([
        path('', include('apps.core.urls', namespace='core')),
        path('', include('apps.accounts.urls', namespace='account')),
        path('', include('apps.products.urls', namespace='products')),
        path('', include('apps.orders.urls', namespace='orders')),
        path('', include('apps.payments.urls', namespace='payments')),
        path('', include('apps.wallets.urls', namespace='wallets')),
    ])),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r'^rosetta/', include('rosetta.urls'))]

# Static and media files serving during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
