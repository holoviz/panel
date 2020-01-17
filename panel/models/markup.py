"""
Custom bokeh Markup models.
"""
from __future__ import absolute_import, division, unicode_literals

from bokeh.core.properties import Bool, Int, String
from bokeh.models.widgets import Markup


class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """


class JSON(Markup):
    """
    A bokeh model that renders JSON as tree.
    """

    depth = Int(default=1, help="Depth to which the JSON tree is expanded.")

    hover = Bool(default=False, help="Whether to show a hover preview.")

    theme = String(default='light', help="Whether to expand all JSON nodes.")
