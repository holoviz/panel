"""
The pane module contains PaneBase objects which may render any type of
object as a bokeh model so it can be embedded in a panel. The pane
objects are one of three main components in panel the other two being
layouts and widgets. Panes may render anything including plots, text,
images, equations etc.
"""
from __future__ import absolute_import, division, unicode_literals

from .ace import Ace # noqa
from .base import PaneBase, Pane, panel # noqa
from .equation import LaTeX # noqa
from .deckgl import DeckGL # noqa
from .holoviews import HoloViews # noqa
from .image import GIF, JPG, PNG, SVG # noqa
from .markup import DataFrame, HTML, JSON, Markdown, Str # noqa
from .media import Audio, Video # noqa
from .plotly import Plotly # noqa
from .plot import Bokeh, Matplotlib, RGGPlot, YT # noqa
from .streamz import Streamz # noqa
from .vega import Vega # noqa
from .vtk import VTK, VTKVolume # noqa
