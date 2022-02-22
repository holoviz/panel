"""
Defines a custom MathJax bokeh model to render text using MathJax.
"""

from bokeh.core.properties import String
from bokeh.models import LayoutDOM

from ..io.resources import bundled_files
from ..util import classproperty


class PyIodide(LayoutDOM):
    """
    A bokeh model that runs pyiodide scripts.
    """

    code = String()

    __javascript__ = ["https://cdn.jsdelivr.net/pyodide/v0.19.0/full/pyodide.js"]

    __js_skip__ = {'loadPyodide': __javascript__}

    __js_require__ = {
        'paths': {
            'mathjax': "//cdn.jsdelivr.net/pyodide/v0.19.0/full/pyodide"
        },
        'shim': {'loadPyiodide': {'exports': "loadPyodide"}}
    }



