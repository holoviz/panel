"""
Defines custom AcePlot bokeh model to render Ace editor.
"""
from __future__ import absolute_import, division, unicode_literals

from bokeh.core.properties import String, Override, Dict, Any, List, Bool, Enum
from bokeh.models import HTMLBox

from ..util import classproperty, bundled_files
from .enums import ace_themes


class AcePlot(HTMLBox):
    """
    A Bokeh model that wraps around a Ace editor and renders it inside
    a Bokeh plot.
    """

    __javascript__ = [
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11/ace.js',
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11/ext-language_tools.js',
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11/ext-modelist.min.js'
    ]

    __js_skip__ = __javascript__

    __js_require__ = {
        'paths': {
            ('ace', ('ace/ace', 'ace/ext-language_tools')): '//cdnjs.cloudflare.com/ajax/libs/ace/1.4.7'},
        'exports': {'ace': 'ace'},
        'shim': {
            'ace/ext-language_tools': { 'deps': ["ace/ace"] },
            'ace/ext-modelist': { 'deps': ["ace/ace"] }
        }
    }

    code = String()

    theme = Enum(ace_themes, default='chrome')

    filename = String()

    language = String()

    annotations = List(Dict(String, Any), default=[])

    readonly = Bool(default=False)

    print_margin = Bool(default=False)

    height = Override(default=300)

    width = Override(default=300)
