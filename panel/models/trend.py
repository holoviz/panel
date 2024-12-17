"""
A Bokeh model indicating trends.
"""
from bokeh.core.properties import Float, Instance, String
from bokeh.models import (
    BasicTickFormatter, NumeralTickFormatter, TickFormatter,
)
from bokeh.models.sources import ColumnDataSource

from .layout import HTMLBox


class TrendIndicator(HTMLBox):
    """
    A Bokeh model indicating trends.
    """

    description = String()
    change_formatter = Instance(
        TickFormatter,
        default=lambda: NumeralTickFormatter(format='0.00%')  # type: ignore
    )
    formatter = Instance(
        TickFormatter,
        default=lambda: BasicTickFormatter()  # type: ignore
    )
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
