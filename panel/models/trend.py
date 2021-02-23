"""
A Bokeh model indicating trends.
"""
from bokeh.core.properties import Instance, Float, String
from bokeh.models import HTMLBox, NumeralTickFormatter, TickFormatter, BasicTickFormatter
from bokeh.models.sources import ColumnDataSource


class TrendIndicator(HTMLBox):
    """
    A Bokeh model indicating trends.
    """

    description = String()
    change_formatter = Instance(TickFormatter, default=lambda: NumeralTickFormatter(format='0.00%'))
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
