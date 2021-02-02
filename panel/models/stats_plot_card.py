"""A Bokeh Model of a Stats Card with a Plot"""
from bokeh.core.properties import Instance, Float, String
from bokeh.models import HTMLBox, TickFormatter, BasicTickFormatter
from bokeh.models.sources import ColumnDataSource


class StatsPlotCard(HTMLBox):
    """A Bokeh Model of a Stats Card with a Plot"""

    description = String()
    formatter = Instance(TickFormatter, default=lambda: BasicTickFormatter())
    layout = String()
    source = Instance(ColumnDataSource)
    plot_x = String()
    plot_y = String()
    plot_color = String()
    plot_type = String()
    pos_color = String()
    neg_color = String()
    title = String()
    value = Float()
    value_change = Float()
