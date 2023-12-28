from bokeh.core.properties import Bool, Int, String
from bokeh.models.widgets import Widget

__all__ = (
    "ToggleIcon",
    "ButtonIcon",
)


class ClickableIcon(Widget):

    active_icon = String(default="", help="""
        The name of the icon to display when toggled.""")

    icon = String(default="heart", help="""
        The name of the icon or SVG to display.""")

    size = String(default="1em", help="""
        The size of the icon as a valid CSS font-size.""")


class ToggleIcon(ClickableIcon):

    value = Bool(default=False, help="""
        Whether the icon is toggled on or off.""")


class ButtonIcon(ClickableIcon):

    clicks = Int(default=0, help="""
        The number of times the button has been clicked.""")

    active_duration = Int(default=75, help="""
        The number of milliseconds the active_icon should be shown for.""")
