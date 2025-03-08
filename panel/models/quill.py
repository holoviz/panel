from bokeh.core.properties import (
    Any, Bool, Either, Enum, List, String,
)

from ..io.resources import bundled_files
from ..util import classproperty
from .layout import HTMLBox


class QuillInput(HTMLBox):
    """
    WYSIWYG text editor based on Quill.js
    """

    __css_raw__ = [
        'https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.bubble.css',
        'https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.snow.css',
    ]

    __javascript_raw__ = [
        'https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.js',
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')

    @classproperty
    def __js_skip__(cls):
        return {'Quill': cls.__javascript__}

    __js_require__ = {
        'paths': {
            'Quill': 'https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill',
        },
        'exports': {
            'Quill': 'Quill'
        }
    }

    mode = Enum("bubble", "toolbar", default='toolbar')

    placeholder = String()

    text = String()

    toolbar = Either(List(Any), Bool)
