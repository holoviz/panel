"""
Defines a custom KaTeXPlot bokeh model to render KaTeX plots. 
"""
import os

from bokeh.models import Markup

from ..util import CUSTOM_MODELS


class KaTeX(Markup):
    """
    A bokeh model that wraps around a plotly plot and renders it inside
    a bokeh plot.
    """

    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js",
                      "https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/contrib/auto-render.min.js"]
    __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]

    __implementation__ = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'katex.ts')


CUSTOM_MODELS['panel.models.plotly.KaTeX'] = KaTeX
