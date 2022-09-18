from collections import OrderedDict

from bokeh.core.properties import (
    Any, Dict, Int, String,
)
from bokeh.events import ModelEvent
from bokeh.models import HTMLBox

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty

XTERM_JS = f"{config.npm_cdn}/xterm@4.14.1/lib/xterm.js"
XTERM_LINKS_JS = f"{config.npm_cdn}/xterm-addon-web-links@0.4.0/lib/xterm-addon-web-links.js"


class KeystrokeEvent(ModelEvent):

    event_name = 'keystroke'

    def __init__(self, model, key=None):
        self.key = key
        super().__init__(model=model)


class Terminal(HTMLBox):
    """Custom Terminal Model"""

    __css_raw__ = [f"{config.npm_cdn}/xterm@4.11.0/css/xterm.css"]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    __javascript_raw__ = [XTERM_JS, XTERM_LINKS_JS]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {
            'xtermjs': cls.__javascript__[0:2],
        }

    __js_require__ = {
        'paths': OrderedDict([
            ("xtermjs", XTERM_JS[:-3]),
            ("xtermjsweblinks", XTERM_LINKS_JS[:-3]),
        ]),
        'exports': {
            "xtermjs": "xtermjs",
            "xtermjsweblinks": "WebLinksAddon",
        },
        'shim': {
            'xtermjsweblinks': {
                'exports': 'WebLinksAddon',
                'deps': ['xtermjs']
            },
        }
    }

    _clears = Int()

    nrows = Int()

    ncols = Int()

    options = Dict(String, Any)

    output = String()
