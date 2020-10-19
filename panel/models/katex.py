"""
Defines a custom KaTeX bokeh model to render text using KaTeX.
"""
from bokeh.models import Markup


class KaTeX(Markup):
    """
    A bokeh model that renders text using KaTeX.
    """

    __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]

    __javascript__ = [
        "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js",
        "https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/contrib/auto-render.min.js"
    ]

    __js_skip__ = {
        'katex': __javascript__[:1],
        'renderMathInElement': __javascript__[1:]
    }

    __js_require__ = {
        'paths': {
            'katex': 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min',
            'autoLoad': 'https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/contrib/auto-render.min'},
        'exports': {'katex': 'katex', 'autoLoad': 'renderMathInElement'}
    }
