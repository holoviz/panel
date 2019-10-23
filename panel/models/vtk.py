# coding: utf-8
"""
Defines custom VTKPlot bokeh model to render VTK objects.
"""
from bokeh.core.properties import String, Bool, Dict, Any, Override
from bokeh.models import HTMLBox

vtk_cdn = "https://unpkg.com/vtk.js"

class VTKPlot(HTMLBox):
    """
    A Bokeh model that wraps around a vtk-js library and renders it inside
    a Bokeh plot.
    """

    __javascript__ = [vtk_cdn]

    __js_require__ = {"paths": {"vtk": vtk_cdn[:-3]},
                      "shim": {"vtk": {"exports": "vtk"}}}

    append = Bool(default=False)

    data = String(help="""The serialized vtk.js data""")

    camera = Dict(String, Any)

    enable_keybindings = Bool(default=False)

    orientation_widget = Bool(default=False)

    renderer_el = Any(readonly=True)

    height = Override(default=300)

    width = Override(default=300)

class VTKVolumePlot(HTMLBox):
    """
    A Bokeh model that wraps around a vtk-js library and renders it inside
    a Bokeh plot.
    """

    __javascript__ = [vtk_cdn]

    __js_require__ = {"paths": {"vtk": vtk_cdn[:-3]},
                      "shim": {"vtk": {"exports": "vtk"}}}

    actor = Any(readonly=True)

    data = Dict(String, Any)

    height = Override(default=300)

    width = Override(default=300)
