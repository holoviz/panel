# Display Content with Panes

In this tutorial, we will learn to display objects with *Panes*:

- *Panes* are available in the `pn.pane` namespace.
- *Panes* take an `object` argument as well as other arguments.
- Discover all *Panes* and their *reference guides* in the [Panes Section](../../reference/index.rst#panes) of the [Component Gallery](../../reference/index.rst).

```python
import panel as pn
pn.extension("echarts", "plotly", "vega", "vizzu")
```

## Display Strings

The `Str` pane can display any text.

Run the code:

```python
import panel as pn

pn.extension()

pn.pane.Str(
    'This is a raw string that will not be formatted in any way.',
).servable()
```

Click [this link](../../reference/panes/Str.md) to the `Str` *reference guide* and spend a few minutes to familiarize yourself with its organization and content.

## Display Markdown

The `Markdown` pane can format and display [*markdown*](https://en.wikipedia.org/wiki/Markdown) strings.

Run the code:

```python
import panel as pn

pn.extension()

pn.pane.Markdown("""\
# Wind Turbine

A wind turbine is a device that converts the kinetic energy of wind into \
[electrical energy](https://en.wikipedia.org/wiki/Electrical_energy).

Read more [here](https://en.wikipedia.org/wiki/Wind_turbine).
""").servable()
```

Click [this link](../../reference/index.rst#panes) to the [Panes Section](../../reference/index.rst#panes) of the [Component Gallery](../../reference/index.rst). Identify the [Markdown Reference Guide](../../reference/panes/Markdown.md) and open it. You don't have to spend time studying the details right now.

### Display Alerts

The `Alert` pane can format and display [*markdown*](https://en.wikipedia.org/wiki/Markdown) strings inside a nicely styled *Alert* pane.

Run the code:

```python
import panel as pn

pn.extension()

pn.pane.Alert("""
## Markdown Sample

This sample text is from [The Markdown Guide](https://www.markdownguide.org)!
""", alert_type="info").servable()
```

## Display Plots

Pick a plotting library below.

:::::{tab-set}

::::{tab-item} Altair
:sync: altair

Run the code below.

```python
import altair as alt
import pandas as pd
import panel as pn

pn.extension("vega")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

fig = (
    alt.Chart(data)
    .mark_line(point=True)
    .encode(
        x="Day",
        y=alt.Y("Wind Speed (m/s)", scale=alt.Scale(domain=(0, 10))),
        tooltip=["Day", "Wind Speed (m/s)"],
    )
    .properties(width="container", height="container", title="Wind Speed")
)

pn.pane.Vega(fig, sizing_mode="stretch_width", height=400).servable()
```

::::

::::{tab-item} ECharts
:sync: echarts

Run the code below.

```python
import panel as pn

pn.extension("echarts")

config = {
    'title': {
        'text': 'Wind Speed'
    },
    "tooltip": {},
    'xAxis': {
        'data': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    },
    'yAxis': {},
    'series': [{
        'name': 'Sales',
        'type': 'line',
        'data': [7, 4, 9, 4, 4, 5, 4]
    }],
}
pn.pane.ECharts(config, height=400, sizing_mode="stretch_width").servable()
```

::::

::::{tab-item} hvPlot
:sync: hvplot

Run the code below.

```python
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn

pn.extension()

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

fig = data.hvplot(x="Day", y="Wind Speed (m/s)", line_width=10, ylim=(0,10), title="Wind Speed")

pn.pane.HoloViews(fig, sizing_mode="stretch_width").servable()
```

::::

::::{tab-item} Matplotlib
:sync: matplotlib

Run the code below.

```python
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import panel as pn

matplotlib.use("agg")

pn.extension()

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

fig, ax = plt.subplots(figsize=(8,3))
ax.plot(
    data["Day"], data["Wind Speed (m/s)"], marker="o", markersize=10, linewidth=4
)
ax.set(
    xlabel="Day",
    ylabel="Wind Speed (m/s)",
    title="Wind Speed",
    ylim=(0, 10),
)
ax.grid()
plt.close(fig)  # CLOSE THE FIGURE TO AVOID MEMORY LEAKS!

pn.pane.Matplotlib(fig, dpi=144, tight=True, format="svg", sizing_mode="stretch_width").servable()
```

::::

::::{tab-item} Plotly
:sync: plotly

Run the code below.

```python
import pandas as pd
import panel as pn
import plotly.express as px

pn.extension("plotly")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

fig = px.line(data, x="Day", y="Wind Speed (m/s)")
fig.update_traces(mode="lines+markers", marker=dict(size=10), line=dict(width=4))
fig.update_yaxes(range=[0, max(data['Wind Speed (m/s)']) + 1])
fig.layout.autosize = True

pn.pane.Plotly(fig, height=400, sizing_mode="stretch_width").servable()
```

::::

::::{tab-item} Vizzu
:sync: vizzu

Run the code below.

```python
import pandas as pd
import panel as pn

pn.extension("vizzu")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

pn.pane.Vizzu(
    data, config={'geometry': 'line', 'x': 'Day', 'y': 'Wind Speed (m/s)', 'title': 'Wind Speed'},
    duration=400, height=400, sizing_mode='stretch_width', tooltip=True
).servable()
```

::::

:::::

## Display a DataFrame

Run the code:

```python
import pandas as pd
import panel as pn

pn.extension()

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 4), ('Sunday', 4)], columns=['Day', 'Orders']
)
pn.pane.DataFrame(data).servable()
```

## Display any Python object

Provides *Panes* to display (almost) any Python object.

Run the code below

```python
import panel as pn

pn.extension()

pn.Column(
    pn.pane.JSON({"Wind Speeds": [0, 3, 6, 9, 12, 15, 18, 21], "Power Output": [0,39,260,780, 1300, 1300, 0, 0]}),
    pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=100),
    pn.pane.Audio("https://assets.holoviz.org/panel/tutorials/wind_turbine.mp3"),
).servable()
```

## Recap

In this guide, we have learned to display Python objects with *Panes*:

- *Panes* are available in the `pn.pane` namespace
- *Panes* take an `object` argument as well as other arguments
- Display strings with the `Str`, `Markdown` and `Alert` panes
- Display plot figures like [Altair](https://altair-viz.github.io/), [ECharts](https://echarts.apache.org/en/index.html), [hvPlot](https://hvplot.holoviz.org), [Matplotlib](https://matplotlib.org/), [Plotly](https://plotly.com/python/) and [Vizzu](https://vizzuhq.com/) with the `Vega`, `ECharts`, `HoloViews`, `Matplotlib`, `Plotly` and `Vizzu` *panes*, respectively.
- Display *DataFrames* with the `DataFrame` and `Perspective` *panes*.
- Add JavaScript dependencies via `pn.extension`. For example `pn.extension("vega")` or `pn.extension("plotly")`
- Discover all *Panes* and their *reference guides* in the [Panes Section](../../reference/index.rst#panes) of the [Component Gallery](../../reference/index.rst).

## Resources

### Tutorials

- [Display objects with `pn.panel`](pn_panel.md)

### How-to

- [Construct Panes](../../how_to/components/construct_panes.md)
- [Migrate from Streamlit | Display Content with Panes](../../how_to/streamlit_migration/panes.md)
- [Style Altair Plots](../../how_to/styling/altair.md)
- [Style Echarts Plots](../../how_to/styling/echarts.md)
- [Style Matplotlib Plots](../../how_to/styling/matplotlib.md)
- [Style Plotly Plots](../../how_to/styling/plotly.md)
- [Style Vega/ Altair Plots](../../how_to/styling/vega.md)

### Explanation

- [Components Overview](../../explanation/components/components_overview.md)

### Component Gallery

- [Panes](../../reference/index.rst#panes)
