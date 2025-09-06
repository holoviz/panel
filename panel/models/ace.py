"""
Defines custom AcePlot bokeh model to render Ace editor.
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Enum, Int, List, Nullable, Override, String,
)

from ..config import config
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
        f"{config.npm_cdn}/ace-builds@1.40.1/src-min-noconflict/ace.js",
        f"{config.npm_cdn}/ace-builds@1.40.1/src-min-noconflict/ext-language_tools.js",
        f"{config.npm_cdn}/ace-builds@1.40.1/src-min-noconflict/ext-modelist.js"
    ]

    __tarball__ = {
        'tar': 'https://registry.npmjs.org/ace-builds/-/ace-builds-1.40.1.tgz',
        'src': 'package/src-min-noconflict/',
        'dest': 'ace-builds@1.40.1/src-min-noconflict'
    }

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {'ace': cls.__javascript__}

    __js_require__ = {
        'paths': {
            ('ace', ('ace/ace', 'ace/ext-language_tools', 'ace/ext-modelist')): "//cdn.jsdelivr.net/npm/ace-builds@1.40.1/src-min-noconflict"},
        'exports': {'ace': 'ace/ace'},
        'shim': {
            'ace/ext-language_tools': { 'deps': ["ace/ace"] },
            'ace/ext-modelist': { 'deps': ["ace/ace"] }
        }
    }

    annotations = List(Dict(String, Any), default=[])

    code = String(default='')

    code_input = String(default='')

    filename = Nullable(String())

    indent = Int(default=4)

    language = String(default='')

    on_keyup = Bool(default=True)

    print_margin = Bool(default=False)

    readonly = Bool(default=False)

    soft_tabs = Bool(default=False)

    theme = Enum(ace_themes, default='github_light_default')

    height = Override(default=300)  # type: ignore

    width = Override(default=300)  # type: ignore
