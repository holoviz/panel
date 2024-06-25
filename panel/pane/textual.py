from __future__ import annotations

import sys

from typing import TYPE_CHECKING, ClassVar

import param

from ..io.state import state
from ..viewable import Viewable
from ..widgets import Terminal
from .base import Pane

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class Textual(Pane):
    """
    The `Textual` pane provides a wrapper around a Textual App component,
    rendering it inside a Terminal and running it on the existing Panel
    event loop, i.e. either on the server or the notebook asyncio.EventLoop.

    Reference: https://panel.holoviz.org/reference/panes/Textual.html

    :Example:

    >>> Textual(app)
    """

    priority: ClassVar[float | bool | None] = 1.0

    _updates: ClassVar[bool] = True

    @classmethod
    def applies(cls, object):
        if 'textual' in sys.modules:
            from textual.app import App
            return isinstance(object, App)
        return False

    def __init__(self, object=None, **params):
        super().__init__(object=object, **params)
        self._terminal = Terminal(**{p: v for p, v in self.param.values().items() if p in Viewable.param})
        self._internal_callbacks.append(
            self.param.watch(self._link_terminal_params, list(Viewable.param))
        )
        self._running_app = None

    def _link_terminal_params(self, *events):
        self._terminal.param.update({event.name: event.new for event in events})

    @param.depends('object', watch=True, on_init=True)
    def _set_driver(self):
        if self.object is None:
            return
        from ._textual import PanelDriver
        self.object.driver_class = PanelDriver
        self.object.__panel__ = self
        self.object._capture_stdout = sys.stdout
        self.object._capture_stderr = sys.stderr

    async def _run_app(self):
        if self._running_app is not None and self._running_app is not self.object:
            await self._running_app._shutdown()
            self._terminal._clear()
        self._running_app = self.object
        await self.object.run_async(size=(self._terminal.ncols, self._terminal.nrows))

    def _on_session_destroyed(self, session_context):
        if not self._models:
            state.execute(self.object._shutdown)

    def _init_app(self, comm):
        if self.object is None or self.object.is_running:
            return
        state.execute(self._run_app)

    def _get_model(
        self, doc: Document, root: Model | None = None,
        parent: Model | None = None, comm: Comm | None = None
    ) -> Model:
        model = self._terminal._get_model(doc, root, parent, comm)
        self._init_app(comm)
        if comm is None:
            doc.on_session_destroyed(self._on_session_destroyed)
        ref = (root or model).ref['id']
        self._models[ref] = (model, parent)
        return model

    def _update_object(
        self, ref: str, doc: Document, root: Model, parent: Model, comm: Comm | None
    ) -> None:
        self._init_app(comm)
