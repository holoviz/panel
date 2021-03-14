import param

from panel.widgets.base import Widget

from ..models import ChartJS as _BkChartJS

# Notes

# - The user needs to specify a height and width if sizing_mode="fixed" and not size given to object

class ChartJS(Widget):
    # Set the Bokeh model to use
    _widget_type = _BkChartJS

    # Rename Panel Parameters -> Bokeh Model properties
    # Parameters like title that does not exist on the Bokeh model should be renamed to None
    _rename = {
        "title": None, "object": "data"
    }

    # Parameters to be mapped to Bokeh model properties
    object = param.Parameter(default=None, doc="""
        The ChartJS object being wrapped. Can be any ChartJS dictionary""")