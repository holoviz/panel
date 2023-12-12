from bokeh.core.properties import Bool
from bokeh.models.ui.icons import TablerIcon

__all__ = (
    "ToggleIcon",
)


class ToggleIcon(TablerIcon):

    value = Bool(default=False, help="""
        Whether the icon is toggled on or off.
        """
    )
