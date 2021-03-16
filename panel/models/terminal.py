from bokeh.core.properties import Int, String
from bokeh.models import HTMLBox

class Terminal(HTMLBox):
    """Custom Terminal Model"""

    object = String()
    clicks = Int()