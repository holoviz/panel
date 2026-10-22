from bokeh.core.properties import (
    Bool, Dict, Enum, Int, List, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models.widgets import InputWidget

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .resource import ExternalResourcesMixin


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


class FileDropper(InputWidget, ExternalResourcesMixin):

    accepted_filetypes = List(String)

    chunk_size = Int(10_000_000)

    max_files = Nullable(Int)

    max_file_size = Nullable(String)

    max_total_file_size = Nullable(String)

    mime_type = Dict(String, String)

    multiple = Bool(True)

    layout = Nullable(Enum("integrated", "compact", "circle", default="compact"))

    previews = List(String)

    # filepond's ESM entrypoint has no default export, so the namespace it
    # resolves to is the same shape as the UMD global; the plugins each
    # default export their plugin object.
    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/filepond@^4/dist/filepond.esm.min.js",
        f"{config.npm_cdn}/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.esm.min.js",
        f"{config.npm_cdn}/filepond-plugin-file-validate-size/dist/filepond-plugin-file-validate-size.esm.min.js",
        f"{config.npm_cdn}/filepond-plugin-file-validate-type/dist/filepond-plugin-file-validate-type.esm.min.js",
        f"{config.npm_cdn}/filepond-plugin-pdf-preview/dist/filepond-plugin-pdf-preview.esm.min.js",
    ]

    __javascript_module_exports__ = [
        'FilePond',
        'FilePondPluginImagePreview',
        'FilePondPluginFileValidateSize',
        'FilePondPluginFileValidateType',
        'FilePondPluginPdfPreview',
    ]

    @classproperty
    def __javascript_modules__(cls):
        return bundled_files(cls, 'javascript_modules')

    @classproperty
    def __js_skip__(cls):
        return {
            'FilePond': cls.__javascript_modules__[:]
        }

    __css_raw__ = [
        f"{config.npm_cdn}/filepond@^4/dist/filepond.css",
        f"{config.npm_cdn}/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css",
        f"{config.npm_cdn}/filepond-plugin-pdf-preview/dist/filepond-plugin-pdf-preview.css"
    ]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')
