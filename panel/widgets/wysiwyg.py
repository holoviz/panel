"""
Defines a WYSIWYG text editor.
"""
import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import Widget


class WYSIWYG(Widget):
    """
    WYSIWYG widget allow editing text.
    """

    disabled = param.Boolean(default=False, doc="""
        Whether the editor is disabled.""")

    placeholder = param.String(doc="Placeholder output when the editor is empty.")

    value = param.String(doc="State of the current text in the editor")

    _rename = {"value": "text", "disabled": "readonly"}

    def __init__(self, **params):
        super().__init__(**params)
        self.jslink(self, readonly='disabled', bidirectional=True)

    def _get_model(self, doc, root=None, parent=None, comm=None):
        if self._widget_type is None:
            self._widget_type = lazy_load(
                'panel.models.quill', 'QuillInput', isinstance(comm, JupyterComm), root
            )
        return super()._get_model(doc, root, parent, comm)
