"""
Defines a custom KaTeX bokeh model to render text using KaTeX.
"""
from bokeh.models import Markup

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .resource import ExternalResourcesMixin

KATEX_VERSION = "0.16.22"

KATEX_FONTS = [
    "AMS-Regular", "Caligraphic-Bold", "Caligraphic-Regular", "Fraktur-Bold",
    "Fraktur-Regular", "Main-Bold", "Main-BoldItalic", "Main-Italic",
    "Main-Regular", "Math-BoldItalic", "Math-Italic", "SansSerif-Bold",
    "SansSerif-Italic", "SansSerif-Regular", "Script-Regular", "Size1-Regular",
    "Size2-Regular", "Size3-Regular", "Size4-Regular", "Typewriter-Regular",
]


class KaTeX(Markup, ExternalResourcesMixin):
    """
    A bokeh model that renders text using KaTeX.
    """

    __css_raw__ = [f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/katex.min.css"]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    __resources__ = [
        f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/fonts/KaTeX_{font}.woff2"
        for font in KATEX_FONTS
    ]

    __javascript_raw__ = [
        f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/katex.min.js",
        f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/contrib/auto-render.min.js"
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
            'katex': f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/katex.min",
            'autoLoad': f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/contrib/auto-render.min"
        },
        'exports': {'katex': 'katex', 'autoLoad': 'renderMathInElement'}
    }
