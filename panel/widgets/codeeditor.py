"""
Defines the CodeEditor widget based on Ace.
"""
from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, Mapping, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..models.enums import ace_themes
from ..util import lazy_load
from ..util.warnings import deprecated
from .base import Widget

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class CodeEditor(Widget):
    """
    The CodeEditor widget allows displaying and editing code in the
    powerful Ace editor.

    Reference: https://panel.holoviz.org/reference/widgets/CodeEditor.html

    :Example:

    >>> CodeEditor(value=py_code, language='python', theme='monokai')
    """

    annotations = param.List(default=[], doc="""
        List of annotations to add to the editor.""")

    filename = param.String(doc="Filename from which to deduce language")

    language = param.String(default='text', doc="Language of the editor")

    print_margin = param.Boolean(default=False, doc="""
        Whether to show the a print margin.""")

    readonly = param.Boolean(default=False, doc="""
        Define if editor content can be modified. Alias for disabled.""")

    theme = param.ObjectSelector(default="chrome", objects=list(ace_themes),
                                 doc="Theme of the editor")

    value = param.String(doc="State of the current code in the editor")

    _rename: ClassVar[Mapping[str, str | None]] = {"value": "code", "name": None}

    def __init__(self, **params):
        if 'readonly' in params:
            params['disabled'] = params['readonly']
        elif 'disabled' in params:
            params['readonly'] = params['disabled']
        super().__init__(**params)
        self._internal_callbacks.append(
            self.param.watch(self._update_disabled, ['disabled', 'readonly'])
        )
        self.jslink(self, readonly='disabled', bidirectional=True)

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        if self._widget_type is None:
            self._widget_type = lazy_load(
                'panel.models.ace', 'AcePlot', isinstance(comm, JupyterComm),
                root, ext='codeeditor'
            )
        return super()._get_model(doc, root, parent, comm)

    def _update_disabled(self, *events: param.parameterized.Event):
        for event in events:
            if event.name == 'disabled':
                self.readonly = event.new
            elif event.name == 'readonly':
                self.disabled = event.new


class Ace(CodeEditor):
    def __init__(self, **params):
        deprecated("1.3", "Ace", "CodeEditor")
        super().__init__(**params)
