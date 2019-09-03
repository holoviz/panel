"""
Defines a custom MathJax bokeh model to render text using MathJax. 
"""
import os

from bokeh.models import Markup

from ..compiler import CUSTOM_MODELS


class MathJax(Markup):
    """
    A bokeh model that renders text using MathJax.
    """

    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML"]

    __js_require__ = {
        'paths': {
            'mathjax': "//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS_HTML"
        },
        'shim': {'mathjax': {'exports': "MathJax"}}
    }

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mathjax.ts')


CUSTOM_MODELS['panel.models.mathjax.MathJax'] = MathJax
