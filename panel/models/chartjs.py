from bokeh.core.properties import Dict, String, Any
from bokeh.models import HTMLBox

class ChartJS(HTMLBox):
    """Custom ChartJS Model"""

    data = Dict(String, Any)