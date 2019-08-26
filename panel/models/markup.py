"""
Custom bokeh Markup models.
"""
from __future__ import absolute_import, division, unicode_literals

from bokeh.models.widgets import Markup


class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """
