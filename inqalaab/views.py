from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView


def index_fun(request):
    return render(request, "index.html")
    # return HttpResponse('Yes')
    

class IndexClass(TemplateView):
    template_name = "index.html"
