"""
Defines a custom KaTeX bokeh model to render text using KaTeX.
"""
from bokeh.models import Markup

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty


class KaTeX(Markup):
    """
    A bokeh model that renders text using KaTeX.
    """

    __css_raw__ = [f"{config.npm_cdn}/katex@0.6.0/dist/katex.min.css"]

    __javascript_raw__ = [
        f"{config.npm_cdn}/katex@0.6.0/dist/katex.min.js",
        f"{config.npm_cdn}/katex@0.10.1/dist/contrib/auto-render.min.js"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    @classproperty
    def __js_skip__(cls):
        return {
            'katex': cls.__javascript__[:1],
            'renderMathInElement': cls.__javascript__[1:]
        }

    __js_require__ = {
        'paths': {
            'katex': "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min",
            'autoLoad': f"{config.npm_cdn}/katex@0.10.1/dist/contrib/auto-render.min"
        },
        'exports': {'katex': 'katex', 'autoLoad': 'renderMathInElement'}
    }
