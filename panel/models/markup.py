"""
Custom bokeh Markup models.
"""
from __future__ import absolute_import, division, unicode_literals

import os

from bokeh.models.widgets import Markup

from ..compiler import CUSTOM_MODELS


class HTML(Markup):
    """
    A bokeh model to render HTML markup including embedded script tags.
    """

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'html.ts')


CUSTOM_MODELS['panel.models.markup.HTML'] = HTML
