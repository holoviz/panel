"""
Defines custom AcePlot bokeh model to render Ace editor.
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Enum, List, Nullable, Override, String,
)

from ..io.resources import bundled_files
from ..util import classproperty
from .enums import ace_themes
from .layout import HTMLBox


class AcePlot(HTMLBox):
    """
    A Bokeh model that wraps around a Ace editor and renders it inside
    a Bokeh plot.
    """

    __javascript_raw__ = [
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11/ace.js',
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11/ext-language_tools.js',
        'https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.11/ext-modelist.js'
    ]

    __tarball__ = {
        'tar': 'https://registry.npmjs.org/ace-builds/-/ace-builds-1.4.11.tgz',
        'src': 'package/src-min/',
        'dest': 'ajax/libs/1.4.11',
        'exclude': ['*snippets/*']
    }

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {'ace': cls.__javascript__}

    __js_require__ = {
        'paths': {
            ('ace', ('ace/ace', 'ace/ext-language_tools', 'ace/ext-modelist')): '//cdnjs.cloudflare.com/ajax/libs/ace/1.4.7'},
        'exports': {'ace/ace': 'ace'},
        'shim': {
            'ace/ext-language_tools': { 'deps': ["ace/ace"] },
            'ace/ext-modelist': { 'deps': ["ace/ace"] }
        }
    }

    code = String(default='')

    code_input = String(default='')

    on_keyup = Bool(default=True)

    theme = Enum(ace_themes, default='chrome')

    filename = Nullable(String())

    language = String(default='')

    annotations = List(Dict(String, Any), default=[])

    readonly = Bool(default=False)

    print_margin = Bool(default=False)

    height = Override(default=300)  # type: ignore

    width = Override(default=300)  # type: ignore
