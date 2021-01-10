import random

import panel as pn
from bokeh.models.sources import ColumnDataSource
from panel.widgets.stats_plot_card import StatsPlotCard


def test_constructor():
    return StatsPlotCard(title="Test")


def test_app():
    data = {"x": [1, 2, 3, 4, 5], "y": [3800, 3700, 3800, 3900, 4000]}
    source = ColumnDataSource(data)

    stats_plot_card = StatsPlotCard(
        title="Panel Users",
        value="4,000",
        value2="+5.1%",
        plot_data=source,
        height=200,
        width=200,
    )

    def update_datasource():
        new_x = max(source.data["x"]) + 1
        old_y = source.data["y"][-1]
        new_y = random.uniform(-old_y * 0.05, old_y * 0.05) + old_y * 1.02
        source.stream({"x": [new_x], "y": [new_y]}, rollover=30)

        y = source.data["y"]
        stats_plot_card.value = f"{y[-1]:,.0f}"
        stats_plot_card.value2 = f"{y[-1]/y[0]-1:.0%}"

    settings_panel = pn.Param(
        stats_plot_card,
        parameters=[
            "height",
            "width",
            "sizing_mode",
            "layout",
            "title",
            "plot_color",
            "plot_type",
        ],
        widgets={
            "height": {"widget_type": pn.widgets.IntSlider, "start": 0, "end": 800, "step": 1},
            "width": {"widget_type": pn.widgets.IntSlider, "start": 0, "end": 800, "step": 1},
        },
        sizing_mode="fixed",
        width=400,
    )
    app = pn.Column(
        pn.pane.HTML(
            "<h1>Panel - Streaming to StatsPlotCard<h1>",
            sizing_mode="stretch_width",
            background="black",
            style={"color": "white", "padding": "15px"},
        ),
        pn.Row(pn.WidgetBox(settings_panel), stats_plot_card, sizing_mode="stretch_both"),
        sizing_mode="stretch_both",
    )
    pn.state.add_periodic_callback(update_datasource, period=250)
    return app


if __name__.startswith("bokeh"):
    test_app().servable()
