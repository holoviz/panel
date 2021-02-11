"""
Custom bokeh Markup models.
"""
from bokeh.core.properties import Any, Bool, List
from bokeh.models import HTMLBox

from ..util import classproperty, bundled_files


class JSONEditor(HTMLBox):
    """
    A bokeh model that allows editing JSON.
    """

    data = Any()

    search = Bool(True)

    selection = List(Any)

    templates = List(Any)

    query = Any()

    result = Any()

    __javascript_raw__ = [
        'https://cdn.jsdelivr.net/npm/jsoneditor@9.1.9/dist/jsoneditor.min.js'
    ]

    __css_raw__ = [
        'https://cdn.jsdelivr.net/npm/jsoneditor@9.1.9/dist/jsoneditor.min.css'
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    @classproperty
    def __js_skip__(cls):
        return {'JSONEditor': cls.__javascript__}

    __js_require__ = {
        'paths': {
            'jsoneditor': "//cdn.jsdelivr.net/npm/jsoneditor@9.1.9/dist/jsoneditor.min.js"
        },
        'shim': {'jsoneditor': {'exports': "JSONEditor"}}
    }
