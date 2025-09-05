from bokeh.core.properties import (
    Bool, Dict, Enum, Int, List, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models.widgets import InputWidget

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty


class UploadEvent(ModelEvent):

    event_name = 'upload_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)

class DeleteEvent(ModelEvent):

    event_name = 'delete_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class FileDropper(InputWidget):

    accepted_filetypes = List(String)

    chunk_size = Int(10_000_000)

    max_files = Nullable(Int)

    max_file_size = Nullable(String)

    max_total_file_size = Nullable(String)

    mime_type = Dict(String, String)

    multiple = Bool(True)

    layout = Nullable(Enum("integrated", "compact", "circle", default="compact"))

    previews = List(String)

    __javascript_raw__ = [
        f"{config.npm_cdn}/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.js",
        f"{config.npm_cdn}/filepond-plugin-file-validate-size/dist/filepond-plugin-file-validate-size.js",
        f"{config.npm_cdn}/filepond-plugin-file-validate-type/dist/filepond-plugin-file-validate-type.js",
        f"{config.npm_cdn}/filepond-plugin-pdf-preview/dist/filepond-plugin-pdf-preview.min.js",
        f"{config.npm_cdn}/filepond@^4/dist/filepond.min.js"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    __js_require__ = {
        'paths': {
            "filepond":  f"{config.npm_cdn}/filepond@^4/dist/filepond",
            "filepond-preview-image": f"{config.npm_cdn}/filepond-plugin-image-preview/dist/filepond-plugin-image-preview",
            "filepond-validate-size": f"{config.npm_cdn}/filepond-plugin-file-validate-size/dist/filepond-plugin-file-validate-size",
            "filepond-validate-type": f"{config.npm_cdn}/filepond-plugin-file-validate-type/dist/filepond-plugin-file-validate-type",
            "filepond-preview-pdf": f"{config.npm_cdn}/filepond-plugin-pdf-preview/dist/filepond-plugin-pdf-preview.min",
        },
        'exports': {
            'filepond': 'FilePond',
            'filepond-preview-image': 'FilePondPluginImagePreview',
            'filepond-preview-pdf': 'FilePondPluginPdfPreview',
            'filepond-validate-size': 'FilePondPluginFileValidateSize',
            'filepond-validate-type': 'FilePondPluginFileValidateType'
        }
    }

    @classproperty
    def __js_skip__(cls):
        return {
            'FilePond': cls.__javascript__[:]
        }

    __css_raw__ = [
        f"{config.npm_cdn}/filepond@^4/dist/filepond.css",
        f"{config.npm_cdn}/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css",
        f"{config.npm_cdn}/filepond-plugin-pdf-preview/dist/filepond-plugin-pdf-preview.css"
    ]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')
