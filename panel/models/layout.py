from bokeh.core.properties import (
    Bool, Float, List, Nullable, String,
)
from bokeh.models import Column as BkColumn
from bokeh.models.layouts import LayoutDOM

__all__ = (
    "Card",
    "HTMLBox",
    "Column",
)


class HTMLBox(LayoutDOM):
    """ """


class Column(BkColumn):

    auto_scroll = Bool(False, help="Whether to scroll to the latest row on update.")

    scroll_button_threshold = Float(
        help="""
        Threshold for showing scroll arrow that scrolls to the latest on click.
        The arrow will be hidden if set to 0.
        """,
    )


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
