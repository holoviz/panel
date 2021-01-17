"""A Bokeh Model of a Stats Card with a Plot"""
from bokeh.core.properties import Instance, String
from bokeh.core.property.primitive import Int
from bokeh.models import HTMLBox
from bokeh.models.sources import ColumnDataSource


class StatsPlotCard(HTMLBox):
    """A Bokeh Model of a Stats Card with a Plot"""

    title = String()
    description = String()
    layout = String()
    value = String()
    value_change = String()
    value_change_sign = Int()
    value_change_pos_color = String()
    value_change_neg_color = String()
    plot_data = Instance(ColumnDataSource)
    plot_x = String()
    plot_y = String()
    plot_color = String()
    plot_type = String()
