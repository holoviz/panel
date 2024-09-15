# Display Content with Panes

In this tutorial, we will learn to display objects with *Panes*:

- *Panes* are available in the `pn.pane` namespace.
- *Panes* take an `object` argument as well as other arguments.
- Discover all *Panes* and their *reference guides* in the [Panes Section](../../reference/index.rst#panes) of the [Component Gallery](../../reference/index.rst).

:::{note}
A *Pane* is a component that can display an object. It takes an `object` as an argument.
:::

:::{note}
You might notice a lot of repetition from the previous section regarding `pn.panel`. Don't worry, it's intentional! We're doing this to empower you with the ability to compare and contrast. While `pn.panel` is incredibly user-friendly and versatile, specific Panes allow you to display output with precision and efficiency. This enables you to construct more intricate and high-performing applications.
:::

:::{note}
When we ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook, or in a file `app.py` that is served with `panel serve app.py --dev`.
:::

```{pyodide}
import panel as pn
pn.extension("echarts", "plotly", "vega", "vizzu")
```

## Display Strings

The [`Str`](../../reference/panes/Str.md) pane can display any text.

Run the code:

```{pyodide}
import panel as pn

pn.extension()

pn.pane.Str(
    'This is a raw string that will not be formatted in any way.',
).servable()
```

:::{note}
We add `.servable()` to the component to add it to the app served by `panel serve app.py --dev`. Adding `.servable()` is not needed to display the component in a notebook.
:::

:::{note}
To learn in detail how a pane like `Str` works, refer to its *reference guide*.
:::

Click [this link](../../reference/panes/Str.md) to the `Str` *reference guide* and spend a few minutes to familiarize yourself with its organization and content.

## Display Markdown

The [`Markdown`](../../reference/panes/Markdown.md) pane can format and display [*markdown*](https://en.wikipedia.org/wiki/Markdown) strings.

Run the code:

```{pyodide}
import panel as pn

pn.extension()

pn.pane.Markdown("""\
# Wind Turbine

A wind turbine is a device that converts the kinetic energy of wind into \
[electrical energy](https://en.wikipedia.org/wiki/Electrical_energy).

Read more [here](https://en.wikipedia.org/wiki/Wind_turbine).
""").servable()
```

:::{tip}
It's key for success with Panel to be able to navigate the [Component Gallery](../../reference/index.rst) and use the *reference guides*.
:::

Click [this link](https://panel.holoviz.org/reference/index.html#panes) to the [Panes Section](https://panel.holoviz.org/reference/index.html#panes) of the [Component Gallery](../../reference/index.rst). Identify the [Markdown Reference Guide](../../reference/panes/Markdown.md) and open it. You don't have to spend time studying the details right now.

### Display Alerts

The [`Alert`](../../reference/panes/Alert.md) pane can format and display [*markdown*](https://en.wikipedia.org/wiki/Markdown) strings inside a nicely styled *Alert* pane.

Run the code:

```{pyodide}
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

```{pyodide}
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

:::{note}
Vega is the name of the JavaScript plotting library used by Altair.

We must add `"vega"` as an argument to `pn.extension` in the example to load the Vega Javascript dependencies in the browser.

If we forget to add `"vega"` to `pn.extension`, then the Altair figure might not display.
:::

::::

::::{tab-item} ECharts
:sync: echarts

Run the code below.

```{pyodide}
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

:::{note}
We must add `"echarts"` as an argument to `pn.extension` in the example to load the ECharts Javascript dependencies in the browser.

If we forget to add `"echarts"` to `pn.extension`, then the ECharts figure might not display.
:::

::::

::::{tab-item} hvPlot
:sync: hvplot

Run the code below.

```{pyodide}
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

:::{note}
[hvPlot](https://hvplot.holoviz.org) is the **easy to use** plotting sister of Panel. It works similarly to the familiar [Pandas `.plot` api](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html). hvPlot is built on top of the data visualization library [HoloViews](https://holoviews.org/). hvPlot, HoloViews, and Panel are all part of the [HoloViz](https://holoviz.org/) family.
:::

::::

::::{tab-item} Matplotlib
:sync: matplotlib

Run the code below.

```{pyodide}
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

:::{note}
In the example, we provide the arguments `dpi`, `format` and `tight` to the Matplotlib pane.

The `Matplotlib` pane can display figures from any framework that produces Matplotlib `Figure` objects like Seaborn, Plotnine and Pandas `.plot`.

We can find more details in the [Matplotlib Reference Guide](../../reference/panes/Matplotlib.md).
:::

::::

::::{tab-item} Plotly
:sync: plotly

Run the code below.

```{pyodide}
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

:::{note}
We must add `"plotly"` as an argument to `pn.extension` in the example to load the Plotly JavaScript dependencies in the browser.

If we forget to add `"plotly"` to `pn.extension`, then the Plotly figure might not display.
:::

::::

::::{tab-item} Vizzu
:sync: vizzu

Run the code below.

```{pyodide}
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

:::{note}
We must add `"vizzu"` as an argument to `pn.extension` in the example to load the Vizzu JavaScript dependencies in the browser.

If we forget to add `"vizzu"` to `pn.extension`, then the Vizzu figure might not display.
:::

::::

:::::

## Display a DataFrame

Run the code:

```{pyodide}
import pandas as pd
import panel as pn

pn.extension()

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 4), ('Sunday', 4)], columns=['Day', 'Orders']
)
pn.pane.DataFrame(data).servable()
```

:::{note}
If we want to display larger dataframes, customize the way the dataframes are displayed, or make them more interactive, we can find specialized components in the [Component Gallery](../../reference/index.rst) supporting these use cases. For example, the [Tabulator](../../reference/widgets/Tabulator.md) widget and [Perspective](../../reference/panes/Perspective.md) pane.
:::

## Display any Python object

Provides *Panes* to display (almost) any Python object.

Run the code below

```{pyodide}
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
- Display strings with the [`Str`]((../../reference/panes/Str.md)), [`Markdown`]((../../reference/panes/Markdown.md)) and [`Alert`]((../../reference/panes/Alert.md)) panes
- Display plot figures like [Altair](https://altair-viz.github.io/), [ECharts](https://echarts.apache.org/en/index.html), [hvPlot](https://hvplot.holoviz.org), [Matplotlib](https://matplotlib.org/), [Plotly](https://plotly.com/python/) and [Vizzu](https://vizzuhq.com/) with the [`Vega`](../../reference/panes/Vega.md), [`ECharts`](../../reference/panes/ECharts.md), [`HoloViews`](../../reference/panes/HoloViews.md), [`Matplotlib`](../../reference/panes/Matplotlib.md), [`Plotly`](../../reference/panes/Plotly.md) and [`Vizzu`](../../reference/panes/Vizzu.md) *panes*, respectively.
- Display *DataFrames* with the [`DataFrame`](../../reference/panes/DataFrame.md) and [`Perspective`]((../../reference/panes/Perspective.md)) *panes*.
- Add JavaScript dependencies via `pn.extension`. For example `pn.extension("vega")` or `pn.extension("plotly")`
- Discover all *Panes* and their *reference guides* in the [Panes Section](https://panel.holoviz.org/reference/index.html#panes) of the [Component Gallery](../../reference/index.rst).

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

- [Panes](https://panel.holoviz.org/reference/index.html#panes)
