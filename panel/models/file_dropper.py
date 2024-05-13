from bokeh.core.properties import (
    Enum, Int, Nullable, String,
)
from bokeh.events import ModelEvent
from bokeh.models.widgets import FileInput

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty


class UploadEvent(ModelEvent):

    event_name = 'upload_event'

    def __init__(self, model, data=None):
        self.data = data
        super().__init__(model=model)


class FileDropper(FileInput):

    chunk_size = Int(1000000)

    max_file_size = Nullable(String)

    max_total_file_size = Nullable(String)

    layout = Enum("integrated", "compact", "circle", default="compact")

    __javascript_raw__ = [
        f"{config.npm_cdn}/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.js",
        f"{config.npm_cdn}/filepond-plugin-file-validate-size/dist/filepond-plugin-file-validate-size.js",
        f"{config.npm_cdn}/filepond@^4/dist/filepond.js"
    ]

    @classproperty
    def __javascript__(cls):
        return bundled_files(cls)

    __css_raw__ = [
        f"{config.npm_cdn}/filepond@^4/dist/filepond.css",
        f"{config.npm_cdn}/filepond-plugin-image-preview/dist/filepond-plugin-image-preview.css"
    ]

    @classproperty
    def __css__(cls):
        return bundled_files(cls, 'css')
