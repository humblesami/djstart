import sys
import datetime
import traceback
from .utils import Logs
from django import shortcuts
from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin


def update_site_paths(context):
    context.update({
        'path_start': settings.URL_PREFIX,
        'site_url': settings.SITE_URL,
        'static_url': settings.STATIC_URL,
        'media_url': settings.MEDIA_URL,
    })
    if not context['path_start'].startswith('/'):
        context['path_start'] += '/'


original_render = shortcuts.render


def updated_render(request, template_name, context=None, content_type=None, status=None, using=None):
    update_site_paths(context)
    return original_render(request, template_name, context, content_type, status, using)


class General(MiddlewareMixin):
    error_message = ''
    
    def process_request(self, request):
        zone = None
        session = getattr(request, 'session', None)
        if session:
            zone = session.get('TIMEZONE_SESSION')
        if zone:
            timezone.activate(zone)
            
    def process_template_response(self, request, response):
        if hasattr(response, 'data'):
            update_site_paths(response.data)
        elif hasattr(response, 'context_data'):
            update_site_paths(response.context_data)
        return response

    def process_response(self, request, response):
        if response.status_code in [404, 410, 500]:
            err_code = response.status_code
            context = {}
            up = settings.URL_PREFIX
            links = [{'name': 'Home', 'link': up}]
            if request.path.startswith(up + 'admin'):
                links.append({'name': 'Admin', 'link': up + 'admin'})
            err_message = self.error_message or 'Server error'
            if err_code == 404:
                err_message = 'Page not found'
            if err_code == 410:
                err_message = 'Requested resource is no more available'
            temp_code = 'general'
            context['links'] = links
            context['message'] = err_message
            temp = 'errors/' + temp_code + '.html'
            response = shortcuts.render(request, temp, context)
            response.status_code = err_code
            return response

        if not settings.DEBUG:
            return response
        cache_age = (60 * 3)
        stale_time = (60 * 60 * 24)
        try:
            cache_age = settings.CACHE_AGE
            stale_time = settings.STALE_TIME
        except:
            pass
        host_name = request.headers['Host']
        if not (host_name.startswith('127.0.0.1') or host_name.startswith('localhost')):
            cache = f'public, max-age={cache_age}, stale-while-revalidate={stale_time},must-revalidate'
            response['Cache-Control'] = cache
        return response

    def process_exception(self, request, exception):
        error_message = str(exception)
        if not error_message.startswith("<class 'django.http.response.Http"):
            self.error_message = error_message + '--' + str(datetime.datetime.now())
            eg = traceback.format_exception(*sys.exc_info())
            error_message = ''
            for er in eg:
                if not 'lib/python' in er and not 'lib\site-packages' in er:
                    error_message += " " + er
            Logs.write_file('Exception => ' + error_message)


shortcuts.render = updated_render
