"""
Defines a WYSIWYG TextEditor widget based on quill.js.
"""
from __future__ import annotations

import typing as t

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from .base import Widget

if t.TYPE_CHECKING:
    from collections.abc import Mapping

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

    mode: t.Literal['bubble', 'toolbar'] = param.Selector(
        default='toolbar', objects=['bubble', 'toolbar'], doc="""
        Whether to display a toolbar or a bubble menu on highlight.""")  # type: ignore[assignment, ty:invalid-assignment]

    on_keyup = param.Boolean(default=True, doc="""
        Whether to update the value on every key press or only upon loss of focus / hotkeys.""")

    toolbar = param.ClassSelector(default=True, class_=(list, bool), doc="""
        Toolbar configuration either as a boolean toggle or a configuration
        specified as a list.""")

    placeholder = param.String(doc="Placeholder output when the editor is empty.")

    selection = param.Dict(default={}, doc="""
        The current text selection in the editor, as ``{"text": "..."}`` when
        the user has a non-empty selection, else ``{}``. Updates live as the
        selection changes.""")

    value = param.String(default="", doc="""
        State of the current text in the editor if `on_keyup`. Otherwise, only upon loss of focus,
        i.e. clicking outside the editor, or pressing <Ctrl+Enter> or <Cmd+Enter>.""")

    value_input = param.String(default="", doc="""
        State of the current text updated on every key press. Identical to `value` if `on_keyup`.""")

    _rename: t.ClassVar[Mapping[str, str | None]] = {
        'label': 'name', 'value': 'text', 'value_input': 'text_input',
    }

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        TextEditor._widget_type = lazy_load(
            'panel.models.quill', 'QuillInput', isinstance(comm, JupyterComm),
            root, ext='texteditor'
        )
        return super()._get_model(doc, root, parent, comm)
