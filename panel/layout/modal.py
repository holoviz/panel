from __future__ import annotations

from typing import (
    TYPE_CHECKING, ClassVar, Mapping, Optional,
)

import param

from pyviz_comms import JupyterComm

from ..io.resources import CDN_DIST
from ..models.modal import ModalDialogEvent
from ..util import lazy_load
from .base import ListPanel

if TYPE_CHECKING:
    from bokeh.document import Document
    from bokeh.model import Model
    from pyviz_comms import Comm


class Modal(ListPanel):
    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    open = param.Boolean(default=False, doc="Whether to open the modal.")

    show_close_button = param.Boolean(default=True, doc="Whether to show a close button in the modal.")

    background_close = param.Boolean(default=True, doc="Whether to enable closing the modal when clicking the background.")

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/models/modal.css"]

    _rename: ClassVar[Mapping[str, str | None]] = {}

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
        self._send_event(ModalDialogEvent, open=self.open)
