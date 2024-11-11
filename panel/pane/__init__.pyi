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
from ._param import (
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

__all__ = [
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
]
