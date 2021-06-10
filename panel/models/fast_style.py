from bokeh.core.properties import String, Int
from bokeh.models import HTMLBox

class FastStyle(HTMLBox):
    """Example implementation of a Custom Bokeh Model"""
    provider = String()

    background_color = String()
    neutral_color = String()
    accent_base_color = String()
    corner_radius = Int()
    body_font = String()

    accent_fill_active = String()
    accent_fill_hover = String()
    accent_fill_rest = String()
    accent_foreground_active = String()
    accent_foreground_cut_rest = String()
    accent_foreground_hover = String()
    accent_foreground_rest = String()
    neutral_outline_active = String()
    neutral_outline_hover = String()
    neutral_outline_rest = String()
    neutral_focus = String()
    neutral_foreground_rest = String()

    updates = Int()