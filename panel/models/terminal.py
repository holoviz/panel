from collections import OrderedDict
from bokeh.core.properties import Any, Dict, Int, String
from bokeh.models import HTMLBox
from ..io.resources import bundled_files
from ..util import classproperty

class Terminal(HTMLBox):
    """Custom Terminal Model"""

    __css_raw__ = ["https://unpkg.com/xterm@4.11.0/css/xterm.css"]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    __javascript_raw__ = [
        "https://unpkg.com/xterm@4.11.0/lib/xterm.js",
        "https://unpkg.com/xterm-addon-fit@0.5.0/lib/xterm-addon-fit.js",
        "https://unpkg.com/xterm-addon-web-links@0.4.0/lib/xterm-addon-web-links.js",
        # "https://unpkg.com/xterm@4.11.0/lib/addons/fullscreen/fullscreen.js",
        # "https://unpkg.com/xterm@4.11.0/lib/addons/search/search.js",
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {
            'xtermjs': cls.__javascript__[0:1],
            'xtermjs-fit': cls.__javascript__[1:2],
            'xtermjs-weblinks': cls.__javascript__[2:3],
        }

    __js_require__ = {
        'paths': OrderedDict([
            ("xtermjs", "https://unpkg.com/xterm@4.11.0/lib/xterm"),
            ("xtermjs-fit", "https://unpkg.com/xterm-addon-fit@0.5.0/lib/xterm-addon-fit"),
            ("xtermjs-weblinks", "https://unpkg.com/xterm-addon-web-links@0.4.0/lib/xterm-addon-web-links"),
        ]),
        'exports': {
            "xtermjs": "xtermjs",
            "xtermjs-fit": "xtermjsfit",
            "xtermjs-weblinks": "xtermjsweblinks",},

    }

    options = Dict(String, Any)
    input = String()
    output = String()

    _clears = Int()
    _value_repeats = Int()