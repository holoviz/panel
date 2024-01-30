# Display objects with `pn.panel`

In this guide you will learn to display Python objects easily and dynamically with `pn.panel`:

- Display a string with `pn.panel(some_string)`
- Display plot figures like [Matplotlib](https://matplotlib.org/), [hvPlot](https://hvplot.holoviz.org) and [Plotly](https://plotly.com/python/) with `pn.panel(fig)`
- Display DataFrames with `pn.panel(df)`
- Display most Python objects with `pn.panel(some_python_object)`
- Configure how an object is displayed by giving arguments to `pn.panel`
- Display most Python objects in *layouts* like `pn.Column` with and without the use of `pn.panel`
- Use a specific *Pane* instead of `pn.panel` if performance is key
- Add javascript dependencies via `pn.extension`. For example `pn.extension("plotly")`

:::{note}
When we ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

```{pyodide}
import panel as pn
pn.extension("plotly")
```

## Install the Dependencies

Please make sure [hvPlot](https://hvplot.holoviz.org/index.html), [Matplotlib](https://matplotlib.org/) and [Plotly](https://plotly.com/python/) are installed.

::::{tab-set}

:::{tab-item} conda
:sync: conda

``` bash
conda install -y -c conda-forge hvplot matplotlib plotly
```
:::

:::{tab-item} pip
:sync: pip

``` bash
pip install hvplot matplotlib plotly
```
:::

::::

## Display a String

Run the code:

```{pyodide}
import panel as pn

pn.extension()

pn.panel("Hello World").servable()
```

:::{note}
We add `.servable()` to the component to add it to the app served by `panel serve app.py --autoreload`. Adding `.servable()` is not needed to display the component in a notebook.
:::

:::{note}
`pn.panel` uses a *heuristic* algorithm to determine how to best display the `object` passed as argument. To make this very explicit we will `print` the component in all the examples below.
:::

Run the code:

```{pyodide}
import panel as pn

pn.extension()

component = pn.panel("Hello World")
print(component)

component.servable()
```

:::{note}
Your cell or terminal output should contain `Markdown(str)`. It means `pn.panel` has picked the [`Markdown`](../../reference/panes/Markdown.md) pane to display the `str` object.
:::

Let's verify that *markdown strings* are actually displayed and rendered nicely.

Run the code:

```{pyodide}
import panel as pn

pn.extension()

component = pn.panel("""
# Markdown Sample

This sample text is from [The Markdown Guide](https://www.markdownguide.org)!
""")
print(component)

component.servable()
```

## Display a Matplotlib plot

Run the code below.

```{pyodide}
import panel as pn
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use('agg')

pn.extension()

def create_matplotlib_figure(figsize=(4,3)):
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2 * np.pi * t)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(t, s)

    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='Voltage')
    ax.grid()

    plt.close(fig) # CLOSE THE FIGURE!
    return fig

fig = create_matplotlib_figure()
component = pn.panel(fig, dpi=144, tight=True)
print(component)

component.servable()
```

Please notice `pn.panel` chose a [`Matplotlib`](../../reference/panes/Matplotlib.md) pane to display the Matplotlib figure.

:::{note}
In the example above we provided arguments to `pn.panel`. These will be applied to the *pane* selected by `pn.panel` to display the object. In this example the [`Matplotlib`](../../reference/panes/Matplotlib.md) pane is selected.

The arguments `dpi` and `tight` would not make sense if a string was provided as argument to `pn.panel`. In that case `pn.panel` would pick a [Markdown](../../reference/panes/Markdown.md) *pane* and the exception `TypeError: Markdown.__init__() got an unexpected keyword argument 'dpi'` would be raised.
:::

## Display a hvPlot plot

Run the code below.

```{pyodide}
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn

pn.extension()
np.random.seed(1)

idx = pd.date_range('1/1/2000', periods=1000)
df = pd.DataFrame(np.random.randn(1000, 4), index=idx, columns=list('ABCD')).cumsum()
fig = df.hvplot()

component = pn.panel(fig, sizing_mode="stretch_width")
print(component)

component.servable()
```

Please notice that `pn.panel` chose a [`HoloViews`](../../reference/panes/HoloViews.md) pane to display the [hvPlot](https://hvplot.holoviz.org/user_guide/Customization.html) figure.

:::{note}
[hvPlot](https://hvplot.holoviz.org) is the **easy to use** plotting sister of Panel. It works similarly to the the familiar [Pandas `.plot` api](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html). hvPlot is built on top of the data visualization library [HoloViews](https://holoviews.org/). hvPlot, HoloViews and Panel are all part of the [HoloViz](https://holoviz.org/) family.
:::

## Display a Plotly plot

Run the code below.

```{pyodide}
import pandas as pd
import panel as pn
import plotly.express as px

pn.extension("plotly")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 4), ('Sunday', 4)], columns=['Day', 'Orders']
)

fig = px.line(data, x="Day", y="Orders")
fig.update_traces(mode="lines+markers", marker=dict(size=10), line=dict(width=4))
fig.layout.autosize = True

component = pn.panel(fig, height=400, sizing_mode="stretch_width")
print(component)

component.servable()
```

Please notice that `pn.panel` chose a [`Plotly`](../../reference/panes/Plotly.md) pane to display the Plotly figure.

:::{note}
We must add `"plotly"` as an argument to `pn.extension` in the example to load the Plotly Javascript dependencies in the browser.

If we forget to add `"plotly"` to `pn.extension` then the Plotly figure will not display in

- a notebook
- a served app. But only if the Plotly figure is displayed dynamically after the app has loaded.
:::

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
component = pn.panel(data)
print(component)
component.servable()
```

```{note}
If you want to display larger dataframes, customize the way the dataframes are displayed or make them more interactive you can find specialized components in the [Component Gallery](../../reference/index.md) supporting these use cases. For example the [Tabulator](../../reference/widgets/Tabulator.md) widget and [Perspective](../../reference/panes/Perspective.md) pane.
```

## Display any Python object

`pn.panel` can display (almost) any Python object.

Run the code below

```{pyodide}
import panel as pn

pn.extension()

component = pn.Column(
    pn.panel({"a": [1,2,3], "b": "some text"}),
    pn.panel("https://assets.holoviz.org/panel/samples/png_sample.png", height=100),
    pn.panel("https://assets.holoviz.org/panel/samples/beatboxing.mp3"),
)
print(component)

component.servable()
```

## Display any Python object in a layout

Run the code below

```{pyodide}
import panel as pn

pn.extension()

component = pn.Column(
    {"a": [1,2,3], "b": "some text"},
    "https://assets.holoviz.org/panel/samples/png_sample.png",
    "https://assets.holoviz.org/panel/samples/beatboxing.mp3",
)
print(component)

component.servable()
```

:::{note}
When Python objects are given as an argument to a Panel [Layout](../../reference/index.md#layouts) like [`pn.Column`](../../reference/layouts/Column.md), then `pn.Column` will automatically apply `pn.panel` to the objects for you.
:::

Please notice that the image of the dice is very tall. To finetune the way it is displayed we can use `pn.panel`.

Run the code below

```{pyodide}
import panel as pn

pn.extension()

component = pn.Column(
    {"a": [1,2,3], "b": "some text"},
    pn.panel("https://assets.holoviz.org/panel/samples/png_sample.png", height=100),
    pn.panel("https://assets.holoviz.org/panel/samples/beatboxing.mp3", styles={"background": "orange", "padding": "10px"}),
)
print(component)

component.servable()
```

## Consider Performance

:::{note}
`pn.panel` is an easy to use and flexible **helper function** that will convert an object into a [*Pane*](../../reference/index.md#panes).

More specifically `pn.panel` resolves the appropriate *representation* for an object by checking all [*Pane*](../../reference/index.md#panes) object types available and then ranking them by priority. When passing a string (for instance) there are many representations, but the [`PNG`](../../reference/panes/PNG.md) pane takes precedence if the string is a valid URL or local file path ending in `.png`.

Resolving the appropriate *representation* for an object takes time. So if performance is key you should specify the specific type of *Pane* to use directly. i.e. use `pn.pane.Matplotlib(fig)` instead of `pn.panel(fig)`.
:::

Run the code below

```{pyodide}
import panel as pn
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use('agg')
pn.extension()

def create_matplotlib_figure(figsize=(4,3)):
    t = np.arange(0.0, 2.0, 0.01)
    s = 1 + np.sin(2 * np.pi * t)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(t, s)

    ax.set(xlabel='time (s)', ylabel='voltage (mV)',
           title='Voltage')
    ax.grid()

    plt.close(fig) # CLOSE THE FIGURE!
    return fig

fig = create_matplotlib_figure()
pn.pane.Matplotlib(fig, dpi=144, tight=True).servable()
```

## Recap

In this guide you have learned to display Python objects easily with `pn.panel`:

- Display a string with `pn.panel(some_string)`
- Display plot figures like Matplotlib, hvPlot and Plotly with `pn.panel(fig)`
- Display most Python objects with `pn.panel(some_python_object)`
- Display DataFrames with `pn.panel(df)`
- Configure how an object is displayed by giving arguments to `pn.panel`
- Display most Python objects in *layouts* like `pn.Column` with and without the use of `pn.panel`
- Use a specific *Pane* instead of `pn.panel` if performance is key
- Add javascript dependencies via `pn.extension`. For example `pn.extension("plotly")`

## Resources

### Tutorials

- [Display objects with Panes](.md)

### How-to

- [Access Pane Type](../../how_to/components/pane_type.md)
- [Construct Panes](../../how_to/components/construct_panes.md)
- [Style Components](../../how_to/styling/index.md)

### Component Gallery

- [Panes](../../reference/index.md#panes)
