from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Mapping

import param

from ..io.resources import CDN_DIST
from ..models import Modal as BkModal
from ..models.layout import ModalDialogEvent
from .base import ListPanel

if TYPE_CHECKING:
    from bokeh.model import Model


class Modal(ListPanel):
    height = param.Integer(default=None, bounds=(0, None))

    width = param.Integer(default=None, bounds=(0, None))

    is_open = param.Boolean(default=False, doc="Whether the modal is open.")

    show_close_button = param.Boolean(default=True, doc="Whether to show a close button in the modal.")

    _bokeh_model: ClassVar[type[Model]] = BkModal

    _stylesheets: ClassVar[list[str]] = [f"{CDN_DIST}css/models/modal.css"]
    _rename: ClassVar[Mapping[str, str | None]] = {}

    def open(self):
        self._send_event(ModalDialogEvent, open=True)

    def close(self):
        self._send_event(ModalDialogEvent, open=False)
