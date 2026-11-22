"""
Defines the CodeEditor widget based on Ace.
"""
from __future__ import annotations

import typing as t

import param

from pyviz_comms import JupyterComm

from ..config import config
from ..models.enums import ace_themes
from ..util import lazy_load
from .base import Widget

_MARKER_TYPES = ('fullLine', 'screenLine', 'text')


def _is_row(value: t.Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


class _Markers(param.List):
    """A list of CodeEditor markers, validated before it is stored."""

    def _validate(self, val):
        super()._validate(val)
        for marker in val or []:
            start = marker.get('start_row')
            if not _is_row(start):
                raise ValueError(
                    f"CodeEditor markers require a non-negative integer 'start_row', got {marker!r}."
                )
            end = marker.get('end_row', start)
            if not _is_row(end) or end < start:
                raise ValueError(
                    f"CodeEditor marker 'end_row' must be an integer >= 'start_row', got {marker!r}."
                )
            if marker.get('type', 'fullLine') not in _MARKER_TYPES:
                raise ValueError(
                    f"CodeEditor marker 'type' must be one of {_MARKER_TYPES}, got {marker!r}."
                )


if t.TYPE_CHECKING:
    from collections.abc import Mapping

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

    annotations: list[dict[str, t.Any]] = param.List(default=[], item_type=dict, doc="""
        List of annotations to add to the editor.""")  # type: ignore[assignment, ty:invalid-assignment]

    filename = param.String(doc="Filename from which to deduce language")

    language = param.String(default='text', doc="Language of the editor")

    indent = param.Integer(default=4, doc="The default indent size.")

    keyboard_accessible = param.Boolean(default=False, doc="""
        Whether Tab moves the focus out of the editor rather than indenting.
        The editor is entered with Enter and left with Escape, so a keyboard
        user is not trapped in it.""")

    markers: list[dict[str, t.Any]] = _Markers(default=[], item_type=dict, doc="""
        List of markers highlighting ranges of rows. Each marker is a dict
        with a zero-based ``start_row``, an optional inclusive ``end_row``
        (defaults to ``start_row``), an optional CSS ``class`` for the
        highlight (defaults to ``pn-ace-marker``, set it to ``None`` to only
        mark the gutter), an optional ``gutter_class`` added to the gutter
        cell of every marked row, and an optional ``type``: ``'fullLine'``
        (default), ``'screenLine'`` or ``'text'``, where a text marker spans
        ``start_column`` to ``end_column``. Setting the parameter replaces
        all previous markers. Markers stay at the rows they were set on and
        do not follow edits, so recompute and set them when the text
        changes.""")  # type: ignore[assignment, ty:invalid-assignment]

    on_keyup = param.Boolean(default=True, doc="""
        Whether to update the value on every key press or only upon loss of focus / hotkeys.""")

    print_margin = param.Boolean(default=False, doc="""
        Whether to show the a print margin.""")

    readonly = param.Boolean(default=False, doc="""
        Define if editor content can be modified. Alias for disabled.""")

    soft_tabs = param.Boolean(default=False, doc="Whether to use spaces instead of tabs.")

    soft_wrap = param.Boolean(default=False, doc="Whether to wrap long lines.")

    theme: str = param.Selector(
        default="github_light_default", objects=list(ace_themes), doc="""
        If no value is provided, it defaults to the current theme
        set by pn.config.theme, as specified in the
        CodeEditor.THEME_CONFIGURATION dictionary. If not defined there, it
        falls back to the default parameter value.""")  # type: ignore[assignment, ty:invalid-assignment]

    value = param.String(default="", doc="""
        State of the current code in the editor if `on_keyup`. Otherwise, only upon loss of focus,
        i.e. clicking outside the editor, or pressing <Ctrl+Enter> or <Cmd+Enter>.""")

    value_input = param.String(default="", doc="""
        State of the current code updated on every key press. Identical to `value` if `on_keyup`.""")

    _rename: t.ClassVar[Mapping[str, str | None]] = {
        "value": "code", "value_input": "code_input", "name": None, "label": None,
    }

    THEME_CONFIGURATION: t.ClassVar[dict[str,str]] = {"dark": "github_dark", "default": "github_light_default"}

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
