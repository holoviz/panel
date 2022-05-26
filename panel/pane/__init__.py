"""
Panel panes renders the Python objects you know and love ❤️
===========================================================

Panes may render anything including plots, text,
images, equations etc.

For example Panel contains Bokeh, HoloViews,
Matplotlib and Plotly panes.

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
from .alert import Alert  # noqa
from .base import Pane, PaneBase, panel  # noqa
from .deckgl import DeckGL  # noqa
from .echarts import ECharts  # noqa
from .equation import LaTeX  # noqa
from .holoviews import HoloViews, Interactive  # noqa
from .idom import IDOM  # noqa0
from .image import (  # noqa
    GIF, ICO, JPG, PDF, PNG, SVG,
)
from .ipywidget import IPyWidget  # noqa
from .markup import (  # noqa
    HTML, JSON, DataFrame, Markdown, Str,
)
from .media import Audio, Video  # noqa
from .perspective import Perspective  # noqa
from .plot import (  # noqa
    YT, Bokeh, Matplotlib, RGGPlot,
)
from .plotly import Plotly  # noqa
from .streamz import Streamz  # noqa
from .vega import Vega  # noqa
from .vtk import VTK, VTKVolume  # noqa

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
    "IDOM",
    "Interactive",
    "IPyWidget",
    "JPG",
    "JSON",
    "LaTeX",
    "Markdown",
    "Matplotlib",
    "Pane",
    "PaneBase",
    "panel",
    "PDF",
    "Perspective",
    "Plotly",
    "PNG",
    "RGGPlot",
    "Str",
    "Streamz",
    "SVG",
    "Vega",
    "Video",
    "VTK",
    "VTKVolume",
    "YT"
)
