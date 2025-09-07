"""
Defines the CodeEditor widget based on Ace.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, ClassVar

import param

from pyviz_comms import JupyterComm

from ..config import config
from ..models.enums import ace_themes
from ..util import lazy_load
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

    indent = param.Integer(default=4, doc="The default indent size.")

    on_keyup = param.Boolean(default=True, doc="""
        Whether to update the value on every key press or only upon loss of focus / hotkeys.""")

    print_margin = param.Boolean(default=False, doc="""
        Whether to show the a print margin.""")

    readonly = param.Boolean(default=False, doc="""
        Define if editor content can be modified. Alias for disabled.""")

    soft_tabs = param.Boolean(default=False, doc="Whether to use spaces instead of tabs.")

    theme = param.Selector(default="github_light_default", objects=list(ace_themes), doc="""
        If no value is provided, it defaults to the current theme
        set by pn.config.theme, as specified in the
        CodeEditor.THEME_CONFIGURATION dictionary. If not defined there, it
        falls back to the default parameter value.""")

    value = param.String(default="", doc="""
        State of the current code in the editor if `on_keyup`. Otherwise, only upon loss of focus,
        i.e. clicking outside the editor, or pressing <Ctrl+Enter> or <Cmd+Enter>.""")

    value_input = param.String(default="", doc="""
        State of the current code updated on every key press. Identical to `value` if `on_keyup`.""")

    _rename: ClassVar[Mapping[str, str | None]] = {"value": "code", "value_input": "code_input", "name": None}

    THEME_CONFIGURATION: ClassVar[dict[str,str]] = {"dark": "github_dark", "default": "github_light_default"}

    def __init__(self, **params):
        if 'readonly' in params:
            params['disabled'] = params['readonly']
        elif 'disabled' in params:
            params['readonly'] = params['disabled']
        if "theme" not in params:
            params["theme"]=self._get_theme(config.theme)
        super().__init__(**params)
        self._internal_callbacks.append(
            self.param.watch(self._update_disabled, ['disabled', 'readonly'])
        )
        self.jslink(self, readonly='disabled', bidirectional=True)

    @param.depends("value", watch=True)
    def _update_value_input(self):
        self.value_input = self.value

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        CodeEditor._widget_type = lazy_load(
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

    @classmethod
    def _get_theme(cls, config_theme: str)->str:
        return cls.THEME_CONFIGURATION.get(config_theme, cls.param.theme.default)
