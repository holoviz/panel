"""
Custom bokeh Markup models.
"""

from bokeh.models.widgets import Markup

from ..util import public

@public
class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """
