from django import shortcuts
from django.conf import settings
from django.views.generic import TemplateView


def is_staff(request, context):
    if request.user:
        if request.user.is_staff:
            pp = settings.PATH_PREFIX or '/'
            context['admin_url'] = pp + 'admin/'
    return context


def index_fun(request):
    context = is_staff(request, {})
    resp2 = shortcuts.render(request, "website/index.html", context)
    return resp2
    # return HttpResponse('Yes')
    

class IndexClass(TemplateView):
    template_name = "website/index.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = is_staff(self.request, context)
        return context
