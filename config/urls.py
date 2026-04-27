from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import Http404
from django.urls import include, path


def disabled_admin_path(request):
    raise Http404()


urlpatterns = [
    path('admin/', disabled_admin_path),
    path('wr-control/', admin.site.urls),

    path('panel/', include('panel.urls')),

    path('', include('core.urls')),
    path('auth/', include('accounts.urls')),
    path('servers/', include('servers.urls')),
    path('shop/', include('shop.urls')),
    path('news/', include('news.urls')),
    path('rules/', include('rules.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)