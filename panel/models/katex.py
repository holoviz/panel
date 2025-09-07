"""
Defines a custom KaTeX bokeh model to render text using KaTeX.
"""
from bokeh.models import Markup

from ..config import config

KATEX_VERSION = "0.16.22"


class KaTeX(Markup):
    """
    A bokeh model that renders text using KaTeX.
    """

    __css__ = [f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/katex.min.css"]

    __javascript__ = [
        f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/katex.min.js",
        f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/contrib/auto-render.min.js"
    ]

    __js_skip__ = {
        'katex': __javascript__[:1],
        'renderMathInElement': __javascript__[1:]
    }

    __js_require__ = {
        'paths': {
            'katex': f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/katex.min",
            'autoLoad': f"{config.npm_cdn}/katex@{KATEX_VERSION}/dist/contrib/auto-render.min"
        },
        'exports': {'katex': 'katex', 'autoLoad': 'renderMathInElement'}
    }
