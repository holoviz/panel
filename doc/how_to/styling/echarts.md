# Style Echarts Plots

This guide addresses how to style ECharts plots displayed using the [ECharts pane](../../../examples/reference/panes/ECharts.ipynb).

You can select the theme of ECharts plots using the `ECharts.theme` parameter.

![ECharts Themes](https://private-user-images.githubusercontent.com/42288570/285575991-657708f5-258a-40c6-88ff-455611ce4d56.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTEiLCJleHAiOjE3MDA5MDMwNjAsIm5iZiI6MTcwMDkwMjc2MCwicGF0aCI6Ii80MjI4ODU3MC8yODU1NzU5OTEtNjU3NzA4ZjUtMjU4YS00MGM2LTg4ZmYtNDU1NjExY2U0ZDU2LmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFJV05KWUFYNENTVkVINTNBJTJGMjAyMzExMjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjMxMTI1VDA4NTkyMFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTcyYmQ5OWUwMDdlMzNhZjBkNzY4NmRjZmE1YWY3NzlmMzFmMDhkNGUwZmRkY2RhNTRkOWU3ZmVjZDZkMTM5MDcmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.z5psS-vgSTDWyGq6kAiLjuXR59zSZ8Y1p_FrGHs08hA)

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
