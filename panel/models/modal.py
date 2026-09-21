
import typing as t

from bokeh.core.properties import Bool
from bokeh.events import ModelEvent
from bokeh.model import Model

from ..config import config
from ..io.resources import bundled_files
from ..util import classproperty
from .layout import Column
from .resource import ExternalResourcesMixin

__all__ = (
    "Modal",
    "ModalDialogEvent",
)


class Modal(Column, ExternalResourcesMixin):

    __javascript_modules_raw__ = [
        f"{config.npm_cdn}/a11y-dialog@7/dist/a11y-dialog.esm.min.js"
    ]

    __javascript_module_exports__ = ['A11yDialog']

    @classproperty
    def __javascript_modules__(cls):
        return bundled_files(cls, 'javascript_modules')

    @classproperty
    def __js_skip__(cls):
        return {'A11yDialog': cls.__javascript_modules__[:1]}

    open = Bool(default=False, help="Whether or not the modal is open.")
    show_close_button = Bool(True, help="Whether to show a close button in the modal.")
    background_close = Bool(True, help="Whether to enable closing the modal when clicking the background.")


class ModalDialogEvent(ModelEvent):
    event_name = 'modal-dialog-event'

    def __init__(self, model: Model | None, open: bool):
        self.open = open
        super().__init__(model=model)

    def event_values(self) -> dict[str, t.Any]:
        return dict(super().event_values(), open=self.open)
