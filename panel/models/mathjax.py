"""
Defines a custom MathJax bokeh model to render text using MathJax. 
"""
import os

from bokeh.models import Markup

from ..util import CUSTOM_MODELS


class MathJax(Markup):
    """
    A bokeh model that renders text using MathJax.
    """

    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML"]

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'mathjax.ts')


CUSTOM_MODELS['panel.models.mathjax.MathJax'] = MathJax
