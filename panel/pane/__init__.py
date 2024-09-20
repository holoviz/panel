"""
Panel panes renders the Python objects you know and love ❤️
===========================================================

Panes may render anything including plots, text, images, equations etc.

For example Panel contains Bokeh, HoloViews, Matplotlib and Plotly panes.

Check out the Panel gallery of panes
https://panel.holoviz.org/reference/index.html#panes for inspiration.

How to use Panel panes in 2 simple steps
----------------------------------------

1. Define your Python objects

>>> some_python_object = ...
>>> another_python_object = ...

2. Define your panes

>>> pn.pane.SomePane(some_python_object).servable()
>>> pn.pane.AnotherPane(another_python_object).servable()

Most often you don't have to wrap your Python object into a specific
pane. Just add your Python object to `pn.panel`, `pn.Column`, `pn.Row` or
other layouts, then Panel will automatically wrap it in the right pane.

For more detail see the Getting Started Guide
https://panel.holoviz.org/getting_started/index.html
"""
from typing import TYPE_CHECKING as _TC

if _TC:
    from ..param import (
        ParamFunction, ParamMethod, ParamRef, ReactiveExpr,
    )
    from .alert import Alert
    from .base import Pane, PaneBase, panel
    from .deckgl import DeckGL
    from .echarts import ECharts
    from .equation import LaTeX
    from .holoviews import HoloViews, Interactive
    from .image import (
        GIF, ICO, JPG, PDF, PNG, SVG, Image, WebP,
    )
    from .ipywidget import IPyLeaflet, IPyWidget, Reacton
    from .markup import (
        HTML, JSON, DataFrame, Markdown, Str,
    )
    from .media import Audio, Video
    from .perspective import Perspective
    from .placeholder import Placeholder
    from .plot import (
        YT, Bokeh, Matplotlib, RGGPlot,
    )
    from .plotly import Plotly
    from .streamz import Streamz
    from .textual import Textual
    from .vega import Vega
    from .vizzu import Vizzu
    from .vtk import VTK, VTKVolume

_attrs = {
    "Alert": "panel.pane.alert:Alert",
    "Audio": "panel.pane.media:Audio",
    "Bokeh": "panel.pane.plot:Bokeh",
    "DataFrame": "panel.pane.markup:DataFrame",
    "DeckGL": "panel.pane.deckgl:DeckGL",
    "ECharts": "panel.pane.echarts:ECharts",
    "GIF": "panel.pane.image:GIF",
    "HoloViews": "panel.pane.holoviews:HoloViews",
    "HTML": "panel.pane.markup:HTML",
    "ICO": "panel.pane.image:ICO",
    "Image": "panel.pane.image:Image",
    "Interactive": "panel.pane.holoviews:Interactive",
    "IPyWidget": "panel.pane.ipywidget:IPyWidget",
    "IPyLeaflet": "panel.pane.ipywidget:IPyLeaflet",
    "JPG": "panel.pane.image:JPG",
    "JSON": "panel.pane.markup:JSON",
    "LaTeX": "panel.pane.equation:LaTeX",
    "Markdown": "panel.pane.markup:Markdown",
    "Matplotlib": "panel.pane.plot:Matplotlib",
    "Pane": "panel.pane.base:Pane",
    "PaneBase": "panel.pane.base:PaneBase",
    "ParamFunction": "panel.param:ParamFunction",
    "ParamMethod": "panel.param:ParamMethod",
    "ParamRef": "panel.param:ParamRef",
    "panel": "panel.pane.base:panel",
    "PDF": "panel.pane.image:PDF",
    "Perspective": "panel.pane.perspective:Perspective",
    "Placeholder": "panel.pane.placeholder:Placeholder",
    "Plotly": "panel.pane.plotly:Plotly",
    "PNG": "panel.pane.image:PNG",
    "ReactiveExpr": "panel.param:ReactiveExpr",
    "Reacton": "panel.pane.ipywidget:Reacton",
    "RGGPlot": "panel.pane.plot:RGGPlot",
    "Str": "panel.pane.markup:Str",
    "Streamz": "panel.pane.streamz:Streamz",
    "SVG": "panel.pane.image:SVG",
    "Textual": "panel.pane.textual:Textual",
    "Vega": "panel.pane.vega:Vega",
    "Video": "panel.pane.media:Video",
    "Vizzu": "panel.pane.vizzu:Vizzu",
    "WebP": "panel.pane.image:WebP",
    "VTK": "panel.pane.vtk:VTK",
    "VTKVolume": "panel.pane.vtk:VTKVolume",
    "YT": "panel.pane.plot:YT",
    # Imports from panel
    "plot": "panel.pane.plot",
}

def __getattr__(name: str) -> object:
    if name == "no_lazy":
        for attr in _attrs:
            mod = __getattr__(attr)
            if hasattr(mod, "_attrs"):
                getattr(mod._attrs, "no_lazy", None)
        return name
    if name in _attrs:
        import importlib
        mod_name, _, attr_name = _attrs[name].partition(':')
        mod = importlib.import_module(mod_name)
        return getattr(mod, attr_name) if attr_name else mod
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = (
    "Alert",
    "Audio",
    "Bokeh",
    "DataFrame",
    "DeckGL",
    "ECharts",
    "GIF",
    "HoloViews",
    "HTML",
    "ICO",
    "Image",
    "Interactive",
    "IPyWidget",
    "IPyLeaflet",
    "JPG",
    "JSON",
    "LaTeX",
    "Markdown",
    "Matplotlib",
    "Pane",
    "PaneBase",
    "ParamFunction",
    "ParamMethod",
    "ParamRef",
    "panel",
    "PDF",
    "Perspective",
    "Placeholder",
    "Plotly",
    "PNG",
    "ReactiveExpr",
    "Reacton",
    "RGGPlot",
    "Str",
    "Streamz",
    "SVG",
    "Textual",
    "Vega",
    "Video",
    "Vizzu",
    "WebP",
    "VTK",
    "VTKVolume",
    "YT"
)

__dir__ = lambda: list(__all__)
