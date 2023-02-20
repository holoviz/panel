"""
Defines a WYSIWYG TextEditor widget based on quill.js.
"""
from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, Mapping, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import Widget

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class TextEditor(Widget):
    """
    The `TextEditor` widget provides a WYSIWYG
    (what-you-see-is-what-you-get) rich text editor which outputs HTML.

    The editor is built on top of the [Quill.js](https://quilljs.com/) library.

    Reference: https://panel.holoviz.org/reference/widgets/TextEditor.html

    :Example:

    >>> TextEditor(placeholder='Enter some text')
    """

    disabled = param.Boolean(default=False, doc="""
        Whether the editor is disabled.""")

    mode = param.Selector(default='toolbar', objects=['bubble', 'toolbar'], doc="""
        Whether to display a toolbar or a bubble menu on highlight.""")

    toolbar = param.ClassSelector(default=True, class_=(list, bool), doc="""
        Toolbar configuration either as a boolean toggle or a configuration
        specified as a list.""")

    placeholder = param.String(doc="Placeholder output when the editor is empty.")

    value = param.String(doc="State of the current text in the editor")

    _rename: ClassVar[Mapping[str, str | None]] = {
        'name': 'name', 'value': 'text'
    }

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        if self._widget_type is None:
            self._widget_type = lazy_load(
                'panel.models.quill', 'QuillInput', isinstance(comm, JupyterComm),
                root, ext='texteditor'
            )
        return super()._get_model(doc, root, parent, comm)
