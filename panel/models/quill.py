from bokeh.core.properties import Bool, String
from bokeh.models import HTMLBox

from ..io.resources import bundled_files
from ..util import classproperty


class QuillInput(HTMLBox):
    """
    WYSIWYG text editor based on Quill.js
    """

    __css_raw__ = [
        'https://cdn.quilljs.com/1.3.6/quill.snow.css'
    ]
    
    __javascript_raw__ = [
        'https://cdn.quilljs.com/1.3.6/quill.js',
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
            'quill': 'https://cdn.quilljs.com/1.3.6/quill',
        },
        'exports': {
            'quill': 'Quill'
        }
    }

    placeholder = String()

    readonly = Bool(False)

    text = String()
