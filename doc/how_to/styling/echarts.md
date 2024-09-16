# Style Echarts Plots

This guide addresses how to style ECharts plots displayed using the [ECharts pane](../../reference/panes/ECharts.md).

You can select the theme of ECharts plots using the `ECharts.theme` parameter.

![ECharts Themes](https://assets.holoviz.org/panel/gifs/echarts-styles.gif)

## An ECharts plot with a custom theme

In this example we will extend the `themes` available to the `ECharts` pane to the themes listed in the [ECharts Themes Guide](https://echarts.apache.org/en/download-theme.html) and then use one of them.

```{pyodide}
import panel as pn

THEME = "shine"

ECHARTS_THEMES = {
    "infographic": "https://fastly.jsdelivr.net/npm/echarts/theme/infographic.js?_v_=20200710_1",
    "macarons": "https://fastly.jsdelivr.net/npm/echarts/theme/macarons.js?_v_=20200710_1",
    "roma": "https://fastly.jsdelivr.net/npm/echarts/theme/roma.js?_v_=20200710_1",
    "shine": "https://fastly.jsdelivr.net/npm/echarts/theme/shine.js?_v_=20200710_1",
    "vintage": "https://fastly.jsdelivr.net/npm/echarts/theme/vintage.js?_v_=20200710_1",
}

pn.pane.ECharts.param.theme.objects = pn.pane.ECharts.param.theme.objects + list(
    ECHARTS_THEMES
)

pn.extension("echarts", js_files=ECHARTS_THEMES)

echart_bar = {
    "title": {"text": "ECharts Example"},
    "tooltip": {},
    "legend": {"data": ["Sales"]},
    "xAxis": {"data": ["shirt", "cardign", "chiffon shirt", "pants", "heels", "socks"]},
    "yAxis": {},
    "series": [{"name": "Sales", "type": "bar", "data": [5, 20, 36, 10, 10, 20]}],
}

plot = pn.pane.ECharts(
    echart_bar,
    height=500,
    sizing_mode="stretch_width",
    theme=THEME,
)
pn.Column(plot.param.theme, plot, sizing_mode="stretch_width").servable()
```
