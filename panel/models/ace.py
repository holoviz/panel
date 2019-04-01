"""
Defines custom AcePlot bokeh model to render Ace editor.
"""
import os

from bokeh.core.properties import String, Override, Dict, Any, List
from bokeh.models import HTMLBox

from ..compiler import CUSTOM_MODELS

class AcePlot(HTMLBox):
    """
    A Bokeh model that wraps around a Ace editor and renders it inside
    a Bokeh plot.
    """

    __javascript__ = ['https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.3/ace.js']

    __js_require__ = {'paths': {'ace': 'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.3/ace'},
                      'shim': {'ace': 'ace'}}

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ace.ts')

    code = String()

    theme = String(default='chrome')

    language = String(default='python')

    annotations = List(Dict(String, Any))

    height = Override(default=300)

    width = Override(default=300)



CUSTOM_MODELS['panel.models.ace.AcePlot'] = AcePlot
