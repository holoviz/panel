from bokeh.core.properties import Bool, String
from bokeh.models.widgets import Widget

__all__ = (
    "ToggleIcon",
)


class ToggleIcon(Widget):

    icon = String(default="heart", help="""
        The name of the icon to display.""")

    active_icon = String(default="", help="""
        The name of the icon to display when toggled.""")

    value = Bool(default=False, help="""
        Whether the icon is toggled on or off.""")
