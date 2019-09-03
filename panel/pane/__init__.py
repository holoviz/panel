"""
The pane module contains PaneBase objects which may render any type of
object as a bokeh model so it can be embedded in a panel. The pane
objects are one of three main components in panel the other two being
layouts and widgets. Panes may render anything including plots, text,
images, equations etc.
"""
from __future__ import absolute_import, division, unicode_literals

from ..viewable import Viewable
from .base import PaneBase, Pane # noqa
from .equation import LaTeX # noqa
from .holoviews import HoloViews # noqa
from .image import GIF, JPG, PNG, SVG # noqa
from .markup import HTML, Markdown, Str # noqa
from .plotly import Plotly # noqa
from .plot import Bokeh, Matplotlib, RGGPlot, YT # noqa
from .vega import Vega # noqa
from .vtk import VTK # noqa
from .ace import Ace # noqa


def panel(obj, **kwargs):
    """
    Creates a panel from any supplied object by wrapping it in a pane
    and returning a corresponding Panel.

    Arguments
    ---------
    obj: object
       Any object to be turned into a Panel
    **kwargs: dict
       Any keyword arguments to be passed to the applicable Pane

    Returns
    -------
    layout: Viewable
       A Viewable representation of the input object
    """
    if isinstance(obj, Viewable):
        return obj
    if kwargs.get('name', False) is None:
        kwargs.pop('name')
    pane = PaneBase.get_pane_type(obj)(obj, **kwargs)
    if len(pane.layout) == 1 and pane._unpack:
        return pane.layout[0]
    return pane.layout
