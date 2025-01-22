from bokeh.core.properties import (
    Bool, Instance, Int, Nullable, String,
)
from bokeh.models.ui.tooltips import Tooltip
from bokeh.models.widgets import AbstractButton, Widget

__all__ = (
    "ToggleIcon",
    "ButtonIcon",
)


class _ClickableIcon(Widget):
    """
    A ClickableIcon is a clickable icon that toggles between an active
    and inactive state.
    """

    active_icon = String(default="", help="""
        The name of the icon to display when toggled.""")

    icon = String(default="heart", help="""
        The name of the icon or SVG to display.""")

    size = String(default="1em", help="""
        The size of the icon as a valid CSS font-size.""")

    value = Bool(default=False, help="""
        Whether the icon is toggled on or off.""")

    title = String(default="", help="""
        The title of the icon.""")

    tooltip = Nullable(Instance(Tooltip), help="""
        A tooltip with plain text or rich HTML contents, providing general help or
        description of a widget's or component's function.
        """)

    tooltip_delay = Int(500, help="""
        Delay (in milliseconds) to display the tooltip after the cursor has
        hovered over the Button, default is 500ms.
        """)


class ToggleIcon(_ClickableIcon):
    """
    A ToggleIcon is a clickable icon that toggles between an active
    and inactive state.
    """


class ButtonIcon(_ClickableIcon, AbstractButton):  # type: ignore
    """
    A ButtonIcon is a clickable icon that toggles between an active
    and inactive state and keeps track of the number of times it has
    been clicked.
    """

    clicks = Int(default=0, help="""
        The number of times the button has been clicked.""")

    toggle_duration = Int(default=75, help="""
        The number of milliseconds the active_icon should be shown for
        and how long the button should be disabled for.""")
