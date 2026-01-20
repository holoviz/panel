"""
Custom bokeh Markup models.
"""
from bokeh.core.properties import (
    Any, Bool, Dict, Enum, List, Nullable, String,
)
from bokeh.events import ModelEvent

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .layout import HTMLBox


class JSONEditEvent(ModelEvent):

    event_name = 'json_edit'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class JSONEditor(HTMLBox):
    """
    A bokeh model that allows editing JSON.
    """

    css = List(String)

    data = Any()

    menu = Bool(True)

    mode = Enum("tree", "view", "form", "code", "text", "preview", default='tree')

    search = Bool(True)

    selection = List(Any)

    schema = Nullable(Dict(String, Any), default=None)

    templates = List(Any)

    __javascript_raw__ = [
        f"{config.npm_cdn}/jsoneditor@10.2.0/dist/jsoneditor.min.js"
    ]

    __css_raw__ = [
        f"{config.npm_cdn}/jsoneditor@10.2.0/dist/jsoneditor.min.css"
    ]

    __resources__ = [
        f"{config.npm_cdn}/jsoneditor@10.2.0/dist/img/jsoneditor-icons.svg"
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
            'jsoneditor': "//cdn.jsdelivr.net/npm/jsoneditor@10.2.0/dist/jsoneditor.min"
        },
        'exports': {'jsoneditor': 'JSONEditor'},
        'shim': {
            'jsoneditor': {
                'exports': "JSONEditor"
            }
        }
    }
