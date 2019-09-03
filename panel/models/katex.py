"""
Defines a custom KaTeX bokeh model to render text using KaTeX.
"""
import os

from bokeh.models import Markup

from ..compiler import CUSTOM_MODELS


class KaTeX(Markup):
    """
    A bokeh model that renders text using KaTeX.
    """

    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js",
                      "https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/contrib/auto-render.min.js"]

    __js_require__ = {'paths': {'katex': 'https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min',
                                'autoLoad': 'https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/contrib/auto-render.min'},
                      'exports': {'katex': 'katex', 'autoLoad': 'renderMathInElement'}}

    __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'katex.ts')


CUSTOM_MODELS['panel.models.katex.KaTeX'] = KaTeX
