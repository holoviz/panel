"""
Defines custom VTKPlot bokeh model to render VTK objects.
"""
from bokeh.core.enums import enumeration
from bokeh.core.has_props import abstract
from bokeh.core.properties import (
    Any, Bool, Bytes, Dict, Enum, Float, Instance, Int, List, Nullable,
    Override, Positive, String,
)
from bokeh.models import ColorMapper, Model

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .layout import HTMLBox

vtk_cdn = f"{config.npm_cdn}/vtk.js@20.0.1/vtk.js"

class VTKAxes(Model):
    """
    A Bokeh model for axes
    """

    axes_opacity = Float(default=1)

    digits = Int(default=1)

    fontsize = Positive(Int, default=12)

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

    __javascript_raw__ = [vtk_cdn]

    @classproperty
    def __javascript__(cls):
        return bundled_files(AbstractVTKPlot)

    @classproperty
    def __js_skip__(cls):
        return {'vtk': cls.__javascript__}

    __js_require__ = {
        "paths": {"vtk": vtk_cdn[:-3]},
        "shim": {
            "vtk": {"exports": "vtk"},
        }
    }

    axes = Instance(VTKAxes)

    camera = Dict(String, Any)

    color_mappers = List(Instance(ColorMapper))

    height = Override(default=300)

    orientation_widget = Bool(default=False)

    interactive_orientation_widget = Bool(default=False)

    width = Override(default=300)

    annotations = List(Dict(String, Any))



class VTKSynchronizedPlot(AbstractVTKPlot):
    """
    Bokeh model for plotting a VTK render window
    """

    arrays = Dict(String, Bytes)

    arrays_processed = List(String)

    enable_keybindings = Bool(default=False)

    one_time_reset = Bool(default=False)

    rebuild = Bool(default=False, help="""If true when scene change all the render is rebuilt from scratch""")

    scene = Dict(String, Any, help="""The serialized vtk.js scene on json format""")


class VTKJSPlot(AbstractVTKPlot):
    """
    Bokeh model for plotting a 3D scene saved in the `.vtk-js` format
    """

    data = Nullable(String, help="""The serialized vtk.js data""")

    enable_keybindings = Bool(default=False)


class VTKVolumePlot(AbstractVTKPlot):
    """
    Bokeh model dedicated to plot a volumetric object with the help of vtk-js
    """

    ambient = Float(default=0.2)

    colormap = String(help="Colormap Name")

    controller_expanded = Bool(default=True, help="""
        If True the volume controller panel options is expanded in the view""")

    data = Nullable(Dict(String, Any))

    diffuse = Float(default=0.7)

    display_slices = Bool(default=False)

    display_volume = Bool(default=True)

    edge_gradient = Float(default=0.2)

    interpolation = Enum(enumeration('fast_linear','linear','nearest'))

    mapper = Dict(String, Any)

    nan_opacity = Float(default=1)

    render_background = String(default='#52576e')

    rescale = Bool(default=False)

    sampling = Float(default=0.4)

    shadow = Bool(default=True)

    slice_i = Int(default=0)

    slice_j = Int(default=0)

    slice_k = Int(default=0)

    specular = Float(default=0.3)

    specular_power = Float(default=8.)
