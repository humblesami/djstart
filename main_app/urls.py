from django.contrib import admin
from django.conf import settings
from django.views.static import serve
from django.urls import include, re_path
from main_app.settings import STATIC_URL
from django.views.generic.base import RedirectView


def define_urls():
    urls_prefix = settings.PATH_PREFIX or ''
    if urls_prefix:
        urls_prefix += '/'
    media_root = {'document_root': settings.MEDIA_ROOT}
    media_urls = [re_path(r'^' + urls_prefix + 'media/(?P<path>.*)$', serve, media_root)]

    static_root = {'document_root': settings.STATIC_ROOT}
    static_urls = [re_path(r'^' + urls_prefix + 'static/(?P<path>.*)$', serve, static_root)]
    
    fav_path = RedirectView.as_view(url=f'{STATIC_URL}website/favicon.ico')
    favicon_url = [re_path(r'^' + urls_prefix + 'favicon.ico', fav_path)]

    # admin.autodiscover()
    if urls_prefix:
        urls_prefix = r'^'+urls_prefix
    app_urls = [
        re_path(urls_prefix + 'admin/', admin.site.urls),
        re_path(urls_prefix, include('website.urls')),
    ]
    all_urls = media_urls + static_urls + favicon_url + app_urls
    return all_urls


urlpatterns = define_urls()
