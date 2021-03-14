from bokeh.core.properties import Int, String
from bokeh.models import HTMLBox

class ChartJS(HTMLBox):
    """Custom ChartJS Model"""

    object = String()
    clicks = Int()