# Create your views here.
from bokeh.embed import server_document

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


# class SlidersView(TemplateView):
#     template_name = bk_cfg.server_cfg['template']

def sliders(request: HttpRequest) -> HttpResponse:
    script = server_document(request.build_absolute_uri())
    return render(request, "sliders/sliders.html", dict(script=script))

