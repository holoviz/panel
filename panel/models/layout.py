from typing import Any

from bokeh.core.properties import (
    Bool, Int, List, Nullable, Readonly, String,
)
from bokeh.events import ModelEvent
from bokeh.models import Column as BkColumn
from bokeh.models.layouts import LayoutDOM

__all__ = (
    "Card",
    "HTMLBox",
    "Column",
    "Modal",
    "ModalDialogEvent",
)


class HTMLBox(LayoutDOM):
    """ """


class Column(BkColumn):

    scroll_position = Int(
        default=0,
        help="""
        Current scroll position of the Column. Setting this value
        will update the scroll position of the Column. Setting to
        0 will scroll to the top."""
    )

    auto_scroll_limit = Int(
        default=0,
        help="""
        Max pixel distance from the latest object in the Column to
        activate automatic scrolling upon update. Setting to 0
        disables auto-scrolling.""")

    scroll_button_threshold = Int(
        default=0,
        help="""
        Min pixel distance from the latest object in the Column to
        display the scroll button. Setting to 0
        disables the scroll button.""")

    view_latest = Bool(
        default=False,
        help="""
        Whether to scroll to the latest object on init. If not
        enabled the view will be on the first object.""")

class Card(Column):
    active_header_background = Nullable(
        String, help="Background color of active Card header."
    )

    button_css_classes = List(
        String, help="CSS classes to add to the Card collapse button."
    )

    collapsed = Bool(True, help="Whether the Card is collapsed.")

    collapsible = Bool(
        True, help="Whether the Card should have a button to collapse it."
    )

    header_background = Nullable(String, help="Background color of the Card header.")

    header_color = Nullable(String, help="Color of the header text and button.")

    header_css_classes = List(String, help="CSS classes to add to the Card header.")

    header_tag = String("div", help="HTML tag to use for the Card header.")

    hide_header = Bool(False, help="Whether to hide the Card header")

    tag = String("tag", help="CSS class to use for the Card as a whole.")


class Modal(Column):
    __css__ = []

    __javascript__ = [
        "https://cdn.jsdelivr.net/npm/a11y-dialog@7/dist/a11y-dialog.min.js"
    ]

    __js_skip__ = {
        # 'modal': __javascript__[:1],
    }
    __js_require__ = {
        'paths': {
            'modal': "https://cdn.jsdelivr.net/npm/a11y-dialog@7/dist/a11y-dialog.min",
        },
        'exports': {}
    }

    is_open = Readonly(Bool, default=False, help="Whether or not the modal is open.")
    show_close_button = Bool(True, help="Whether to show a close button in the modal")


class ModalDialogEvent(ModelEvent):
    event_name = 'modal-dialog-event'

    def __init__(self, model: ModelEvent, open: bool):
        self.open = open
        super().__init__(model=model)

    def event_values(self) -> dict[str, Any]:
        return dict(super().event_values(), open=self.open)
