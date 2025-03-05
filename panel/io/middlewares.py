from typing import Any, Dict

from bokeh.document import Document
from bokeh.events import Event

from ..reactive import Syncable


class BokehEventMiddleware:
    def preprocess(self, syncable: Syncable, doc: Document, event: Event):
        pass

    def postprocess(self):
        pass


class PropertyChangeEventMiddleware:
    def preprocess(self, syncable: Syncable, doc: Document, events: Dict[str, Any]):
        pass

    def postprocess(self):
        pass
