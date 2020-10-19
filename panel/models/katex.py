"""
Defines a custom KaTeX bokeh model to render text using KaTeX.
"""
from bokeh.models import Markup

from ..util import classproperty, bundled_files


class KaTeX(Markup):
    """
    A bokeh model that renders text using KaTeX.
    """

    __css_raw__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    __javascript_raw__ = [
        "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js",
        "https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/contrib/auto-render.min.js"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __js_skip__(cls):
        return {
            'katex': cls.__javascript__[:1],
            'renderMathInElement': cls.__javascript__[1:]
        }

    __js_require__ = {
        'paths': {
            'katex': 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min',
            'autoLoad': 'https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/contrib/auto-render.min'},
        'exports': {'katex': 'katex', 'autoLoad': 'renderMathInElement'}
    }
