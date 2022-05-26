import random

from panel import (
    Column, Param, Row, WidgetBox, state,
)
from panel.pane import HTML
from panel.widgets import IntSlider, Trend


def test_constructor():
    return Trend(title="Test")


def test_trend_auto_value():
    data = {"x": [1, 2, 3, 4, 5], "y": [3800, 3700, 3800, 3900, 4000]}

    trend = Trend(data=data)

    model = trend.get_root()

    assert model.value == 4000
    assert model.value_change == ((4000/3900) - 1)


def test_trend_auto_value_stream():
    data = {"x": [1, 2, 3, 4, 5], "y": [3800, 3700, 3800, 3900, 4000]}

    trend = Trend(data=data)

    model = trend.get_root()

    trend.stream({'x': [6], 'y': [4100]}, rollover=5)

    assert model.value == 4100
    assert model.value_change == ((4100/4000) - 1)
    assert len(model.source.data['x']) == 5
    assert model.source.data['x'][-1] == 6


def test_app():
    data = {"x": [1, 2, 3, 4, 5], "y": [3800, 3700, 3800, 3900, 4000]}

    trend = Trend(
        title="Panel Users",
        value=4000,
        value_change=0.51,
        data=data,
        height=200,
        width=200,
    )

    def update_datasource():
        new_x = max(data["x"]) + 1
        old_y = data["y"][-1]
        new_y = random.uniform(-old_y * 0.05, old_y * 0.05) + old_y * 1.01
        trend.stream({"x": [new_x], "y": [new_y]}, rollover=50)

        y_series = data["y"]
        trend.value = y_series[-1]
        change = y_series[-1] / y_series[-2] - 1
        trend.value_change = change

    settings_panel = Param(
        trend,
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
            "height": {"widget_type": IntSlider, "start": 0, "end": 800, "step": 1},
            "width": {"widget_type": IntSlider, "start": 0, "end": 800, "step": 1},
        },
        sizing_mode="fixed",
        width=400,
    )
    app = Column(
        HTML(
            "<h1>Panel - Streaming to TrendIndicator<h1>",
            sizing_mode="stretch_width",
            background="black",
            style={"color": "white", "padding": "15px"},
        ),
        Row(WidgetBox(settings_panel), trend, sizing_mode="stretch_both"),
        sizing_mode="stretch_both",
    )
    state.add_periodic_callback(update_datasource, period=50)
    return app


if __name__.startswith("bokeh"):
    test_app().servable()
