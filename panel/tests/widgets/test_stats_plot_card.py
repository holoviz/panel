import random

import panel as pn
from bokeh.models.sources import ColumnDataSource


def test_constructor():
    return pn.indicators.StatsPlotCard(title="Test")


def test_app():
    data = {"x": [1, 2, 3, 4, 5], "y": [3800, 3700, 3800, 3900, 4000]}
    source = ColumnDataSource(data)

    stats_plot_card = pn.indicators.StatsPlotCard(
        title="Panel Users",
        value="4,000",
        value2="+5.1%",
        plot_data=source,
        height=200,
        width=200,
        background="lightgray"
    )

    def update_datasource():
        new_x = max(source.data["x"]) + 1
        old_y = source.data["y"][-1]
        new_y = random.uniform(-old_y * 0.05, old_y * 0.05) + old_y * 1.02
        source.stream({"x": [new_x], "y": [new_y]}, rollover=30)

        y = source.data["y"]
        stats_plot_card.value = f"{y[-1]:,.0f}"
        change = y[-1]/y[-2]-1
        stats_plot_card.value_change = f"{change:.0%}"
        if change>0:
            stats_plot_card.value_change_sign=1
        else:
            stats_plot_card.value_change_sign=-1

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
            "value_change_pos_color",
            "value_change_neg_color",
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
