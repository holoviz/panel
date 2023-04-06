"""
Defines a custom MyST bokeh model to render text using mystjs.
"""
from bokeh.models import Markup


class MyST(Markup):
    """
    A bokeh model that renders text using MySTJS.
    """

    __javascript__ = [
        "https://cdn.jsdelivr.net/npm/mystjs@0.0.15/dist/myst.min.js"
    ]

    __js_skip__ = {'MyST': __javascript__}

    __js_require__ = {
        'paths': {
            'mathjax': "//cdn.jsdelivr.net/npm/mystjs@0.0.15/dist/myst.min"
        }
    }
