"""
Defines a custom MathJax bokeh model to render text using MathJax.
"""
from bokeh.models import Markup

from ..util import classproperty, bundled_files


class MathJax(Markup):
    """
    A bokeh model that renders text using MathJax.
    """

    __javascript_raw__ = [
        "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    __js_skip__ = {'MathJax': __javascript__}

    __js_require__ = {
        'paths': {
            'mathjax': "//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS_HTML"
        },
        'shim': {'mathjax': {'exports': "MathJax"}}
    }
