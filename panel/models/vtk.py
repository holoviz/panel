# coding: utf-8
"""
Defines custom VTKPlot bokeh model to render VTK objects.
"""
import os

from bokeh.core.properties import String, Bool, Dict, Any, Instance, Override
from bokeh.models import HTMLBox, Model

from ..widgets import StaticText

vtk_cdn = "https://unpkg.com/vtk.js@13.5.0/dist/vtk.js"
#vtk_cdn = "http://localhost:8080/vtk.js"
jszip_cdn = "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.5/jszip.js"

class VTKPlot(HTMLBox):
    """
    A Bokeh model that wraps around a vtk-js library and renders it inside
    a Bokeh plot.
    """

    __javascript__ = [vtk_cdn, jszip_cdn]

    __js_require__ = {"paths": {"vtk": vtk_cdn[:-3],
                                "jszip": jszip_cdn[:-3]},
                      "exports": {"jszip": "jszip"},
                      "shim": {"vtk": {"exports": "vtk"}}}

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'vtk.ts')

    append = Bool(default=False)

    scene = String(help="""The serialized vtk.js scene""")

    arrays = Dict(String, Any)

    camera = Dict(String, Any)

    enable_keybindings = Bool(default=False)

    height = Override(default=300)

    width = Override(default=300)

