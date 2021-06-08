from collections import OrderedDict

from bokeh.core.properties import Any, Dict, Int, String
from bokeh.models import HTMLBox

from ..io.resources import bundled_files
from ..util import classproperty


XTERM_JS = "https://unpkg.com/xterm@4.11.0/lib/xterm.js"
XTERM_LINKS_JS = "https://unpkg.com/xterm-addon-web-links@0.4.0/lib/xterm-addon-web-links.js"


class Terminal(HTMLBox):
    """Custom Terminal Model"""

    options = Dict(String, Any)
    input = String()
    output = String()

    _clears = Int()
    _value_repeats = Int()

    __css_raw__ = ["https://unpkg.com/xterm@4.11.0/css/xterm.css"]

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
            'xtermjs': cls.__javascript__[0:1],
            'xtermjs-weblinks': cls.__javascript__[2:3],
        }

    __js_require__ = {
        'paths': OrderedDict([
            ("xtermjs", XTERM_JS[:-3]),
            ("xtermjs-weblinks", XTERM_LINKS_JS[:-3]),
        ]),
        'exports': {
            "xtermjs": "xtermjs",
            "xtermjs-weblinks": "xtermjsweblinks",},
    }
