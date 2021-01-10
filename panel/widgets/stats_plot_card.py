"""The StatsPlotCard enables the user to display a Dashboard KPI Card with

- Title: The name or a short title
- Value: Primary Value to display. For example an absolute value.
- Value2: A secondary value. For example a percentage change.
- Plot: A plot. One of line", "step", "area", "bar

The card can be layout out as

- a column (text and plot on top of each other) or
- a row (text and plot after each other)
"""
import param
from bokeh.models.sources import ColumnDataSource
from panel.models.stats_plot_card import StatsPlotCard as _BkStatsPlotCard
from panel.widgets.base import Widget


class StatsPlotCard(Widget):
    """The StatsPlotCard enables the user to display a Dashboard KPI Card with

    - Title: The name or a short title
    - Value: Primary Value to display. For example an absolute value.
    - Value2: A secondary value. For example a percentage change.
    - Plot: A plot. One of line", "step", "area", "bar

    The card can be layout out as

    - a column (text and plot on top of each other) or
    - a row (text and plot after each other)
    """
    _widget_type = _BkStatsPlotCard

    _rename = {}

    title = param.String(doc="""The title or a short description of the card""")
    layout = param.ObjectSelector(default="column", objects=["column"])
    value = param.String(doc="""The primary value to be displayed""")
    value2 = param.String(doc="""A secondary value to display together with the primary value""")
    plot_data = param.ClassSelector(
        class_=ColumnDataSource,
        doc="""A ColumnDataSource on the form
            ColumnDataSource(data=dict(x=[10, 20, 30], y=[100, 200, 300]))
        """,
    )
    plot_x = param.String(
        default="x", doc="The name of the key in the plot_data to use on the x-axis"
    )
    plot_y = param.String(
        default="y", doc="The name of the key in the plot_data to use on the y-axis"
    )
    plot_color = param.String(default="firebrick", doc="the color to use in the plot")
    plot_type = param.ObjectSelector(
        default="bar", objects=["line", "step", "area", "bar"], doc="the color to use in the plot"
    )
