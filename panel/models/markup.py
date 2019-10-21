"""
Custom bokeh Markup models.
"""

from bokeh.models.widgets import Markup


class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """
