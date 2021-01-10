"""A Bokeh Model of a Stats Card with a Plot"""
from bokeh.core.properties import Instance, String
from bokeh.models import HTMLBox
from bokeh.models.sources import ColumnDataSource


class StatsPlotCard(HTMLBox):
    """A Bokeh Model of a Stats Card with a Plot"""

    title = String()
    description = String()
    layout = String()
    value = String()
    value2 = String()
    plot_data = Instance(ColumnDataSource)
    plot_x = String()
    plot_y = String()
    plot_color = String()
    plot_type = String()
