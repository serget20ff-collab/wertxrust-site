from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from accounts import views as accounts_views


def favicon_view(request):
    return redirect('/static/favicon.svg', permanent=True)


urlpatterns = [
    path('favicon.ico', favicon_view),

    path('admin/', admin.site.urls),
    path('wr-control/', admin.site.urls),

    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('auth/steam/login/', accounts_views.steam_login, name='legacy_steam_login'),
    path('auth/steam/callback/', accounts_views.steam_callback, name='legacy_steam_callback'),
    path('panel/', include('panel.urls')),
    path('shop/', include('shop.urls')),
    path('servers/', include('servers.urls')),
    path('news/', include('news.urls')),
    path('rules/', include('rules.urls')),
]

if settings.DEBUG or getattr(settings, 'SERVE_MEDIA_FILES', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)