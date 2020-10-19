"""
Defines a custom MathJax bokeh model to render text using MathJax.
"""
from bokeh.models import Markup


class MathJax(Markup):
    """
    A bokeh model that renders text using MathJax.
    """

    __javascript__ = [
        "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
    ]

    __js_skip__ = {'MathJax': __javascript__}

    __js_require__ = {
        'paths': {
            'mathjax': "//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS_HTML"
        },
        'shim': {'mathjax': {'exports': "MathJax"}}
    }
