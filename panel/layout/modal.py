from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, Literal, Mapping, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..util import lazy_load
from ..util.warnings import PanelUserWarning, warn
from .base import ListPanel

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class Modal(ListPanel):
    """Create a modal dialog that can be opened and closed."""

    open = param.Boolean(default=False, doc="Whether to open the modal.")

    show_close_button = param.Boolean(default=True, doc="Whether to show a close button in the modal.")

    background_close = param.Boolean(default=True, doc="Whether to enable closing the modal when clicking the background.")

    _rename: ClassVar[Mapping[str, str | None]] = {}

    _source_transforms: ClassVar[Mapping[str, str | None]] = {'objects': None}

    def _get_model(
        self, doc: Document, root: Optional[Model] = None,
        parent: Optional[Model] = None, comm: Optional[Comm] = None
    ) -> Model:
        Modal._bokeh_model = lazy_load(
            'panel.models.modal', 'Modal', isinstance(comm, JupyterComm), root
        )
        return super()._get_model(doc, root, parent, comm)

    def show(self):
        self.open = True

    def hide(self):
        self.open = False

    def toggle(self):
        self.open = not self.open

    @param.depends("open", watch=True)
    def _open(self):
        from ..models.modal import ModalDialogEvent
        if not self._models:
            msg = "To use the Modal, you must use '.servable' in a server setting or output the Modal in Jupyter Notebook."
            warn(msg, category=PanelUserWarning)
        self._send_event(ModalDialogEvent, open=self.open)

    def create_button(self, action: Literal["show", "hide", "toggle"], **kwargs):
        """Create a button to show, hide or toggle the modal."""
        from panel.widgets import Button

        button = Button(**kwargs)
        match action:
            case "show":
                button.on_click(lambda *e: self.show())
            case "hide":
                button.on_click(lambda *e: self.hide())
            case "toggle":
                button.on_click(lambda *e: self.toggle())
            case _:
                raise TypeError(f"Invalid action: {action}")

        return button
