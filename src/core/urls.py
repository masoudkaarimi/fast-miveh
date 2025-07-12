from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include, re_path
from django.conf.urls.i18n import i18n_patterns

api_urlpatterns = [
    path('api/', include('apps.account.urls', namespace='account')),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),

    path('i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += api_urlpatterns

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [re_path(r'^rosetta/', include('rosetta.urls'))]

# Static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
