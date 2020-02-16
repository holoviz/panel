"""
Defines custom AcePlot bokeh model to render Ace editor.
"""
from __future__ import absolute_import, division, unicode_literals

from bokeh.core.properties import String, Override, Dict, Any, List, Bool, Enum
from bokeh.models import HTMLBox

from .enums import ace_themes


class AcePlot(HTMLBox):
    """
    A Bokeh model that wraps around a Ace editor and renders it inside
    a Bokeh plot.
    """

    __javascript__ = [
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.7/ace.js',
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.7/ext-language_tools.js'
    ]

    __js_skip__ = {'ace': __javascript__}

    __js_require__ = {
        'paths': {
            ('ace', ('ace/ace', 'ace/ext-language_tools')): '//cdnjs.cloudflare.com/ajax/libs/ace/1.4.7'},
        'exports': {'ace': 'ace'},
        'shim': {
            'ace/ext-language_tools': { 'deps': ["ace/ace"] }
        }
    }

    code = String()

    theme = Enum(ace_themes, default='chrome')

    language = String(default='python')

    annotations = List(Dict(String, Any), default=[])

    readonly = Bool(default=False)

    height = Override(default=300)

    width = Override(default=300)
