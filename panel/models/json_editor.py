"""
Custom bokeh Markup models.
"""
from bokeh.core.properties import Any, Bool, List
from bokeh.events import ModelEvent
from bokeh.models import HTMLBox

from ..io.resources import bundled_files
from ..util import classproperty


class JSONEditEvent(ModelEvent):

    event_name = 'json_edit'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class JSONEditor(HTMLBox):
    """
    A bokeh model that allows editing JSON.
    """

    data = Any()

    search = Bool(True)

    selection = List(Any)

    templates = List(Any)

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
