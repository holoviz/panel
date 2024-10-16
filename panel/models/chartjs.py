from bokeh.core.properties import Int, String

from .layout import HTMLBox


class ChartJS(HTMLBox):
    """Custom ChartJS Model"""

    object = String()
    clicks = Int()
