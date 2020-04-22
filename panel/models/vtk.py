# coding: utf-8
"""
Defines custom VTKPlot bokeh model to render VTK objects.
"""
from bokeh.core.properties import (String, Bool, Dict, Any, Override,
                                   Instance, Int, Float, PositiveInt,
                                   Enum, List)
from bokeh.core.has_props import abstract
from bokeh.core.enums import enumeration
from bokeh.models import HTMLBox, Model, ColorMapper

jszip_cdn = "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.5/jszip.js"
vtk_cdn = "http://localhost:8000/vtk.js"


class VTKAxes(Model):
    """
    A Bokeh model for axes
    """

    axes_opacity = Float(default=1)

    digits = Int(default=1)

    fontsize = PositiveInt(default=12)

    grid_opacity = Float(default=0.1)

    origin = Any()

    show_grid = Bool(default=True)

    xticker = Dict(String, Any)

    yticker = Dict(String, Any)

    zticker = Dict(String, Any)


@abstract
class AbstractVTKPlot(HTMLBox):
    """
    Abstract Bokeh model for vtk plots that wraps around a vtk-js library and
    renders it inside a Bokeh plot.
    """

    __javascript__ = [vtk_cdn, jszip_cdn]

    __js_skip__ = {'vtk': [vtk_cdn, jszip_cdn]}

    __js_require__ = {
        "paths": {"vtk": vtk_cdn[:-3],
                  "jszip": jszip_cdn[:-3]},
        "exports": {"vtk": None, "jszip": None},
        "shim": {
            "vtk": {"exports": "vtk"},
            "jszip": {"exports": "jszip"}
        }
    }

    renderer_el = Any(readonly=True)

    axes = Instance(VTKAxes)

    camera = Dict(String, Any)

    color_mappers = List(Instance(ColorMapper))

    height = Override(default=300)

    orientation_widget = Bool(default=False)

    width = Override(default=300)

    axes = Instance(VTKAxes)


class VTKSynchronizedPlot(AbstractVTKPlot):
    """
    TODO
    """

    arrays = Dict(String, Any)

    arrays_processed = List(String)

    enable_keybindings = Bool(default=False)

    one_time_reset = Bool(default=False)

    scene = Dict(String, Any, help="""The serialized vtk.js scene on json format""")


class VTKJSPlot(AbstractVTKPlot):
    """
    Bokeh model dedicated to plot a vtk render window with only 3D geometry objects
    (Volumes are not suported)
    """

    data = String(help="""The serialized vtk.js data""")

    enable_keybindings = Bool(default=False)


class VTKVolumePlot(AbstractVTKPlot):
    """
    Bokeh model dedicated to plot a volumetric object with the help of vtk-js
    (3D geometry objects are not suported)
    """

    ambient = Float(default=0.2)

    colormap = String(help="Colormap Name")

    data = Dict(String, Any)

    diffuse = Float(default=0.7)

    display_slices = Bool(default=False)

    display_volume = Bool(default=True)

    edge_gradient = Float(default=0.2)

    interpolation = Enum(enumeration('fast_linear','linear','nearest'))

    mapper = Dict(String, Any)

    render_background = String(default='#52576e')

    rescale = Bool(default=False)

    sampling = Float(default=0.4)

    shadow = Bool(default=True)

    slice_i = Int(default=0)

    slice_j = Int(default=0)

    slice_k = Int(default=0)

    specular = Float(default=0.3)

    specular_power = Float(default=8.)
