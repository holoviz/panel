from bokeh.core.properties import Bool, String
from bokeh.models.widgets import Widget

__all__ = (
    "ToggleIcon",
)


class ToggleIcon(Widget):

    active_icon = String(default="", help="""
        The name of the icon to display when toggled.""")

    icon = String(default="heart", help="""
        The name of the icon or SVG to display.""")

    size = String(default="1em", help="""
        The size of the icon as a valid CSS font-size.""")

    value = Bool(default=False, help="""
        Whether the icon is toggled on or off.""")
