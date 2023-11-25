# Style Plotly Plots

This guide addresses how to style Plotly plots displayed using the [Plotly pane](../../../examples/reference/panes/Plotly.ipynb).

Plotly provides a list of built in templates in `plotly.io.templates`. See the [Plotly Templates Guide](https://plotly.com/python/templates/).

The gif below displays an example of what can be achieved with a little styling of the Plotly plot and the `FastListTemplate`.

![PlotlyStyle.gif](https://assets.holoviews.org/panel/thumbnails/gallery/styles/plotly-styles.gif)

## A Plotly Express plot with dark theme and accent color

In this example we will give the Plotly Express plot a dark theme and a custom accent color.

```{pyodide}
import pandas as pd
import plotly.express as px

import panel as pn

pn.extension("plotly", sizing_mode="stretch_width")

ACCENT_COLOR = "#F08080"
TEMPLATE = "plotly_dark"  # "ggplot2", "seaborn", "simple_white", "plotly", "plotly_white", "plotly_dark", "presentation", "xgridoff", "ygridoff", "gridon", "none"

data = pd.DataFrame(
    [
        ("Monday", 7),
        ("Tuesday", 4),
        ("Wednesday", 9),
        ("Thursday", 4),
        ("Friday", 4),
        ("Saturday", 4),
        ("Sunday", 4),
    ],
    columns=["Day", "Orders"],
)

fig = px.line(
    data,
    x="Day",
    y="Orders",
    template=TEMPLATE,
    color_discrete_sequence=(ACCENT_COLOR,),
    title=f"Orders: '{TEMPLATE}' theme",
)
fig.update_traces(mode="lines+markers", marker=dict(size=10), line=dict(width=4))
fig.layout.autosize = True

pn.pane.Plotly(fig, height=500, sizing_mode="stretch_width").servable()
```

## A Plotly `go.Figure` plot with dark theme

In this example we will give the Plotly `go.Figure` plot a dark theme.

```{pyodide}
import pandas as pd
import plotly.graph_objects as go

import panel as pn

pn.extension("plotly", sizing_mode="stretch_width")

TEMPLATE = "plotly_dark"  # "ggplot2", "seaborn", "simple_white", "plotly", "plotly_white", "plotly_dark", "presentation", "xgridoff", "ygridoff", "gridon", "none"

z_data = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/api_docs/mt_bruno_elevation.csv")

fig = go.Figure(
    data=go.Surface(z=z_data.values),
    layout=go.Layout(
        title="Mt Bruno Elevation",
    ))
fig.layout.autosize = True
fig.update_layout(template=TEMPLATE, title=f"Mt Bruno Elevation: {TEMPLATE}' theme")

pn.pane.Plotly(fig, height=500, sizing_mode="stretch_width").servable()
```
