from django.shortcuts import render

from bokeh.embed import server_document

from . import bk_config

def sliders(request):
    return render(request, 'base.html', {
        "server_script": server_document('http://%s:%s/bk_sliders_app'%(bk_config.server['address'],
                                                                        bk_config.server['port']))})
