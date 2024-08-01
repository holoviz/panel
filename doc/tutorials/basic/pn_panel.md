# Display Content with `pn.panel`

In this guide, we will learn to display Python objects easily with `pn.panel`:

- Display any Python object via `pn.panel(the_object, ...)`.

:::{note}
When we ask to *run the code* in the sections below, we may execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook, or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

```{pyodide}
import panel as pn
pn.extension("plotly", "vega")
```

## Display a String

To build an app, our first step is to display things. Luckily, Panel provides us with the simple yet powerful `pn.panel()` function. This function effortlessly transforms Python objects into viewable components within our app. Let's start with something simple: a string.

Run the code:

```{pyodide}
import panel as pn

pn.extension()

pn.panel("Hello World").servable()
```

:::{note}
We add `.servable()` to the component to add it to the app served by `panel serve app.py --autoreload`. Adding `.servable()` is not needed to display the component in a notebook.
:::

`pn.panel` uses a *heuristic* algorithm to determine how to best display the `object`. To make this very explicit, we will `print` the component in all the examples below.

Run the code:

```{pyodide}
import panel as pn

pn.extension()

component = pn.panel("Hello World")
print(component)

component.servable()
```

Your cell or terminal output should contain `Markdown(str)`. It means `pn.panel` has picked a [`Markdown`](../../reference/panes/Markdown.md) *pane* to display the `str` object.

Let's verify that *markdown strings* are actually displayed and rendered nicely.

Run the code:

```{pyodide}
import panel as pn

pn.extension()

component = pn.panel("""
# Wind Turbine

A wind turbine is a device that converts the kinetic energy of wind into \
[electrical energy](https://en.wikipedia.org/wiki/Electrical_energy).

Read more [here](https://en.wikipedia.org/wiki/Wind_turbine).
""")
print(component)

component.servable()
```

```{tip}
Markdown rendering is very useful in Panel applications, such as for displaying formatted text, headers, links, images, LaTeX formulas and other rich content
```

## Display a DataFrame

Now that we've mastered the art of displaying strings, let's take it up a notch. In our journey to build a data-centric app, we'll often need to display more complex objects like dataframes. With Panel, it's as easy as pie.

Run the code:

```{pyodide}
import pandas as pd
import panel as pn

pn.extension()

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)
component = pn.panel(data)
print(component)
component.servable()
```

:::{tip}
If we want to display larger dataframes, customize the way the dataframes are displayed, or make them more interactive, we can find specialized components in the [Component Gallery](../../reference/index.md) supporting these use cases. For example, the [Tabulator](../../reference/widgets/Tabulator.md) *widget* and [Perspective](../../reference/panes/Perspective.md) *pane*.
:::

## Display Plots

Many data apps contains one or more plots. Lets try to display some.

Pick a plotting library below.

:::::{tab-set}

::::{tab-item} Altair
:sync: altair

Run the code below:

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
    .properties(width="container", height="container", title="Wind Speed Over the Week")
)

component = pn.panel(fig, sizing_mode="stretch_width", height=400)
print(component)

component.servable()
```

Please notice that `pn.panel` chose a [`Vega`](../../reference/panes/Vega.md) pane to display the [Altair](https://altair-viz.github.io/) figure.

:::{note}
Vega is the name of the JavaScript plotting library used by Altair.

We must add `"vega"` as an argument to `pn.extension` in the example to load the Vega Javascript dependencies in the browser.

If we forget to add `"vega"` to `pn.extension`, then the Altair figure might not display.
:::

::::

::::{tab-item} hvPlot
:sync: hvPlot

Run the code below:

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

fig = data.hvplot(x="Day", y="Wind Speed (m/s)", line_width=10, ylim=(0,10))

component = pn.panel(fig, sizing_mode="stretch_width", )
print(component)

component.servable()
```

Please notice that `pn.panel` chose a [`HoloViews`](../../reference/panes/HoloViews.md) pane to display the [hvPlot](https://hvplot.holoviz.org/user_guide/Customization.html) figure.

:::{note}
[hvPlot](https://hvplot.holoviz.org) is the **easy to use** plotting sister of Panel. It works similarly to the familiar [Pandas `.plot` API](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html). hvPlot is built on top of the data visualization library [HoloViews](https://holoviews.org/). hvPlot, HoloViews, and Panel are all part of the [HoloViz](https://holoviz.org/) family.
:::

::::

::::{tab-item} Matplotlib
:sync: matplotlib

Run the code below:

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
    title="Wind Speed Over the Week",
    ylim=(0, 10),
)
ax.grid()
plt.close(fig)  # CLOSE THE FIGURE TO AVOID MEMORY LEAKS!

component = pn.panel(
    fig, format="svg", dpi=144, tight=True, sizing_mode="stretch_width"
)
print(component)

component.servable()
```

Please notice `pn.panel` chose a [`Matplotlib`](../../reference/panes/Matplotlib.md) pane to display the Matplotlib figure.

:::{note}
In the example above we provided arguments to `pn.panel`. These will be applied to the *pane* selected by `pn.panel` to display the object. In this example the [`Matplotlib`](../../reference/panes/Matplotlib.md) pane is selected.

The arguments `dpi`, `format` and `tight` would not make sense if a string was provided as an argument to `pn.panel`. In that case, `pn.panel` would pick a [Markdown](../../reference/panes/Markdown.md) *pane* and the exception `TypeError: Markdown.__init__() got an unexpected keyword argument 'dpi'` would be raised.
:::

::::

::::{tab-item} Plotly
:sync: plotly

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

component = pn.panel(fig, height=400, sizing_mode="stretch_width")
print(component)

component.servable()
```

Please notice that `pn.panel` chose a [`Plotly`](../../reference/panes/Plotly.md) pane to display the Plotly figure.

:::{note}
We must add `"plotly"` as an argument to `pn.extension` in the example to load the Plotly Javascript dependencies in the browser.

If we forget to add `"plotly"` to `pn.extension`, then the Plotly figure might not display.
:::

::::

:::::

## Display any Python object

`pn.panel` can display (almost) any Python object.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

component = pn.Column(
    pn.panel({"Wind Speeds": [0, 3, 6, 9, 12, 15, 18, 21], "Power Output": [0,39,260,780, 1300, 1300, 0, 0]}),
    pn.panel("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=100),
    pn.panel("https://assets.holoviz.org/panel/tutorials/wind_turbine.mp3"),
)
print(component)

component.servable()
```

## Display any Python object in a layout

If we place objects in a [*layout*](https://panel.holoviz.org/reference/index.html#layouts) like [`pn.Column`](../../reference/layouts/Column.md) (more about layouts later), then the layout will apply `pn.panel` for us automatically.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

component = pn.Column(
    {"Wind Speeds": [0, 3, 6, 9, 12, 15, 18, 21], "Power Output": [0,39,260,780, 1300, 1300, 0, 0]},
    "https://assets.holoviz.org/panel/tutorials/wind_turbine.png",
    "https://assets.holoviz.org/panel/tutorials/wind_turbine.mp3",
)
print(component)

component.servable()
```

Please notice that the image of the wind turbine is quite large. To fine-tune the way it is displayed, we can use `pn.panel` with arguments.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

component = pn.Column(
    pn.panel({"Wind Speeds": [0, 3, 6, 9, 12, 15, 18, 21], "Power Output": [0,39,260,780, 1300, 1300, 0, 0]}),
    pn.panel("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=100),
    pn.panel("https://assets.holoviz.org/panel/tutorials/wind_turbine.mp3", styles={"background": "orange", "padding": "10px"}),
)
print(component)

component.servable()
```

:::{note}
The example above sets the *css* `styles` of the `Audio` player. The `styles` parameter is introduced in the [Styles](style.md) tutorial.
:::

## Consider Performance

`pn.panel` is a versatile helper function that converts objects into a [*Pane*](https://panel.holoviz.org/reference/index.html#panes). It automatically selects the best *representation* for an object based on available [*Pane*](https://panel.holoviz.org/reference/index.html#panes) types, ranking them by priority.

For optimal performance, specify the desired *Pane* type directly, like `pn.pane.Matplotlib(fig)` instead of using `pn.panel(fig)`. You will learn about *Panes*  in the [Display Content with Panes](panes.md) section.

## Recap

In this guide, we have learned to display Python objects easily with `pn.panel`:

- Display a string with `pn.panel(some_string)`
- Display plot figures like [Altair](https://altair-viz.github.io/), [hvPlot](https://hvplot.holoviz.org), [Matplotlib](https://matplotlib.org/) and [Plotly](https://plotly.com/python/) with `pn.panel(fig)`
- Display DataFrames with `pn.panel(df)`
- Display most Python objects with `pn.panel(some_python_object)`
- Configure how an object is displayed by giving arguments to `pn.panel`
- Display most Python objects in *layouts* like `pn.Column` with and without the use of `pn.panel`
- Use a specific *Pane* instead of `pn.panel` if performance is key
- Add JavaScript dependencies via `pn.extension`. For example `pn.extension("vega")` or `pn.extension("plotly")`

## Resources

### Tutorials

- [Display objects with Panes](panes.md)

### How-to

- [Access Pane Type](../../how_to/components/pane_type.md)
- [Construct Panes](../../how_to/components/construct_panes.md)
- [Style Components](../../how_to/styling/index.md)

### Component Gallery

- [Panes](https://panel.holoviz.org/reference/index.html#panes)
