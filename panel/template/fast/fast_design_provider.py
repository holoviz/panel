from panel.widgets import Widget
from ...models.fast_design_provider import FastDesignProvider as _BkFastDesignProvider
import param

READ_ONLY_COLORS = [
    "accent_fill_active",
    "accent_fill_hover",
    "accent_fill_rest",
    "accent_foreground_rest",
    "accent_foreground_hover",
    "accent_foreground_active",
    "accent_foreground_cut_rest",
    "neutral_outline_rest",
    "neutral_outline_hover",
    "neutral_outline_active",
    "neutral_focus",
    "neutral_foreground_rest",
]

class FastDesignProvider(Widget):
    """

    See https://www.fast.design/docs/api/fast-components.fastdesignsystemprovider and
    https://color.fast.design/
    """
    _widget_type = _BkFastDesignProvider
    _rename = {
        "title": None
    }
    provider = param.ObjectSelector(default="body-design-provider", objects=["body-design-provider", "header-design-provider"])

    # The three colors to change
    background_color = param.Color(
        doc="""This is the contextual color used by the design system to determine what color it
        is rendering on"""
    )
    neutral_color = param.Color(
        doc="""Defines the base color the neutral palette and all netral colors are derived from"""
    )
    accent_base_color = param.Color(
        doc="""Defines the base color the accent palette and all accent colors are derived from"""
    )
    corner_radius = param.Integer(bounds=(0,25))
    body_font = param.String()

    # Accent recipes use the accent palette and are intended to bring attention or otherwise
    # distinguish the element on the page.
    accent_fill_active = param.Color(
        constant=True,
        doc="Used as the fill of an accent fill element when active.",
    )
    accent_fill_hover = param.Color(
        constant=True,
        doc="Used as the fill of an accent fill element when hovered.",
    )
    accent_fill_rest = param.Color(
        constant=True,
        doc="Used as the fill of an accent element at rest.",)

    accent_foreground_rest = param.Color(constant=True,)
    accent_foreground_hover = param.Color(constant=True)
    accent_foreground_active = param.Color(constant=True)
    accent_foreground_cut_rest = param.Color(constant=True)


    neutral_outline_rest = param.Color(
        constant=True,
        doc="Used as a rest outline color for outline controls."
    )
    neutral_outline_hover = param.Color(
        constant=True,
        doc="Used as the outline of a neutralOutline control when hovered."
    )
    neutral_outline_active = param.Color(
        constant=True,
        doc="Used as the outline of a neutralOutline control when active."
    )

    neutral_focus = param.Color(
        constant=True,
        doc="The color of the focus indicator when the element has document focus.")
    neutral_foreground_rest = param.Color(
        constant=True,
        doc="Primary page text color when the text is in a rest state."
    )

    updates = param.Integer(
        constant=True,
        doc="""An incremented value signals that the colors have been updated. Watching this
        parameter might be much more efficient than watching all colors and reacting to each
        individual change."""
    )
    def __init__(self, **params):
        params["sizing_mode"]="fixed"
        params["width"]=0
        params["height"]=0
        params["margin"]=0
        params["background"]="blue"
        super().__init__(**params)


    def _add_color(self, name):
        color = getattr(self, name)
        return f"<span style='white-space: nowrap;width:300px;display:inline-block'><div style='background: {color};height:1em;width:1em;display: inline-block;'></div><span style=''>&nbsp;{name} {color}</span></span> "

    def to_html(self) -> str:
        """Returns html displaying the parameters"""
        # if not self.accent_fill_active:
        #     return "Nothing"
        html = ""
        colors = [color for color in READ_ONLY_COLORS if getattr(self, color)]
        html += "".join([self._add_color(color) for color in colors])
        return html