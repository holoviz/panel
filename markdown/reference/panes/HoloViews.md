# HoloViews
---
```python
import holoviews as hv
import panel as pn

hv.extension("bokeh", "plotly")
```

[HoloViews](https://holoviews.org/) is a popular and powerful data visualization library supporting many data and plotting *backends*.

[hvPlot](https://hvplot.holoviz.org/index.html) (quick viz) and [GeoViews](https://holoviz.org/assets/geoviews.png) (spatial viz) are built on top of HoloViews and produces `HoloViews` objects.

**Panel, HoloViews, hvPlot and GeoViews are all members of the [HoloViz](https://holoviz.org) ecosystem and you can expect them to work perfectly together**.

In this reference notebook we will assume a basic level of understanding of HoloViews and optionally hvPlot or Geoviews if you want to use them with Panel.

---

The `HoloViews` pane renders [HoloViews](https://holoviews.org/) objects with one of the *plotting backends* supported by HoloViews. This includes objects produced by [hvPlot](https://hvplot.holoviz.org/index.html) and [GeoViews](https://holoviz.org/assets/geoviews.png).

The `HoloViews` pane supports displaying interactive `HoloMap` and `DynamicMap` objects containing widgets. The `HoloViews` pane even allows customizing the widget types and their position relative to the plot.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

The main argument is the `object` parameter

* **`object`** (object): The HoloViews object being displayed

You can control the way the `object` is rendered and sharing axes with other plots via the parameters

* **`backend`** (str): Any of the supported HoloViews backends ('bokeh', 'matplotlib', or 'plotly'). If none is specified defaults to the active holoviews renderer. This is by default 'bokeh'.
* **`linked_axes`** (boolean, default=True): Whether to link axes across plots in a panel layout
* **`format`** (str, default='png'): The output format to use when plotting a Matplotlib plot.
* **`renderer`**: Explicit [HoloViews Renderer](https://holoviews.org/user_guide/Plots_and_Renderers.html#renderers) instance to use for rendering the HoloViews  plot. Overrides the` backend` parameter.
* **`theme` (str, Theme)**: [Bokeh theme](https://docs.bokeh.org/en/latest/docs/reference/themes.html) to apply to the HoloViews plot.

You can access the layout and (optional) widgets via

* **`layout`** (pn.layout.Panel): The layout containing the plot pane and (optionally) the `widget_box` layout.
* **`widget_box`** (ListPanel): The layout containing the widgets

##### Layout and Widget Parameters

The below parameters are used to control the layout and widgets when using `pn.panel` or `pn.pane.HoloViews(...).layout`.

* **`center`** (boolean, default=False): Whether to center the plot or not.
* **`default_widgets`** (dict): Mapping that determines which widgets are used by default when constructing interactive controls for HoloViews dimensions.
    Keys and expected values:

    - `'date'`: For datetime ranges.
    - `'discrete'`: For categorical values.
    - `'discrete_numeric'`: For discrete, numeric values.
    - `'float'`: For continuous floating-point ranges.
    - `'int'`: For integer ranges.
    - `'scrubber'`: For stepping through frame sequences.

    Note that the type may defined as a tuple to offer
    different widgets for  static case (i.e. a `HoloMap`) and
    the dynamic case (i.e. a `DynamicMap`).
* **`widgets`** (dict, argument): A mapping from dimension name to a widget class, instance, or dictionary of overrides to modify the default widgets. Provided as an argument.
* **`widget_location`** (str): Where to lay out the widget relative to the plot
* **`widget_layout`** (ListPanel): The object to lay the widgets out in, one of `Row`, `Column` or `WidgetBox`
* **`widget_type`** (str): Whether to generate individual widgets for each dimension, or to use a global linear scrubber with dimensions concatenated.
___

The `pn.pane.HoloViews` pane will automatically convert any ``HoloViews`` object into a displayable panel, while keeping all of its interactive features:

```python
import numpy as np

data = {"group": np.random.randint(0, 10, 100), "value": np.random.randn(100)}
box = hv.Scatter(data, kdims="group", vdims="value").sort().opts()

hv_pane = pn.pane.HoloViews(box, height=300, sizing_mode="stretch_width")
hv_pane
```

By setting the pane's ``object`` the plot can be updated like all other pane objects:

```python
hv_pane.object = hv.Violin(box).opts(violin_color='Group', responsive=True, height=300)
```

You can display [hvPlot](https://hvplot.holoviz.org/) (and [GeoViews](https://geoviews.org/)) objects too because they are `HoloViews` objects.

```python
import pandas as pd
import hvplot.pandas

df = pd.DataFrame(data)
plot = df.hvplot.box(by="group", y="value", responsive=True, height=300)
pn.pane.HoloViews(plot, height=300, sizing_mode="stretch_width")
```

You can also display `HoloMap` and `DynamicMap` objects.

[HoloViews](https://holoviews.org/) (the framework) natively renders plots with widgets if a `HoloMap` or [DynamicMap](https://holoviews.org/reference/containers/bokeh/DynamicMap.html) declares any *key dimensions*. This approach efficiently updates just the data inside a plot instead of replacing the plot entirely.

```python
import pandas as pd
import hvplot.pandas
import holoviews.plotting.bokeh

def sine(frequency=1.0, amplitude=1.0, function='sin'):
    xs = np.arange(200)/200*20.0
    ys = amplitude*getattr(np, function)(frequency*xs)
    return pd.DataFrame(dict(y=ys), index=xs).hvplot(height=250, responsive=True)

dmap = hv.DynamicMap(sine, kdims=['frequency', 'amplitude', 'function']).redim.range(
    frequency=(0.1, 10), amplitude=(1, 10)).redim.values(function=['sin', 'cos', 'tan'])

hv_panel = pn.pane.HoloViews(dmap)
hv_panel
```

The `layout` parameter contains the `HoloViews` pane and the `widget_box`.

```python
print(hv_panel.layout, "\n\n", hv_panel.widget_box)
```

## Backend

The ``HoloViews`` pane will default to the 'bokeh' plotting backend if no backend has been loaded via `holoviews`, but you can change the backend to any of the 'bokeh', 'matplotlib' and 'plotly' backends as needed.

### Bokeh

Bokeh is the default plotting backend, so normally you don't have to specify it. But lets do it here to show how it works.

```python
plot = df.hvplot.scatter(x="group", y="value")
pn.pane.HoloViews(plot, backend='bokeh', sizing_mode="stretch_width", height=300)
```

### Matplotlib

The Matplotlib backend allows generating figures for print and publication. If you want to allow for responsive sizing you can set `format='svg'` and then use the standard responsive `sizing_mode` settings:

```python
hvplot.extension("matplotlib")

plot = df.hvplot.scatter(x="group", y="value")

pn.pane.HoloViews(plot, backend='matplotlib', sizing_mode="stretch_both", format='svg', center=False)
```

Please note that in a *server context* you might have to set the matplotlib backend like below depending on your setup.

```python
import matplotlib
matplotlib.use('agg')
```

### Plotly

To use the 'plotly' plotting backend you will need to run `hv.extension("plotly")` to configure the 'plotly' backend.

If you are using `hvPlot` you can use `hvplot.extension("plotly")` instead.

```python
hvplot.extension("plotly")

plot = df.hvplot.scatter(x="group", y="value", height=300, responsive=True)

pn.pane.HoloViews(plot, backend='plotly', height=300)
```

Lets change the default backend back to 'bokeh'

```python
hvplot.extension("bokeh")
```

### Dynamic

You can change the plotting backend dynamically via a widget too.

```python
plot = df.hvplot.scatter(x="group", y="value", height=300, responsive=True, title="Try changing the backend")

plot_pane = pn.pane.HoloViews(plot, backend='bokeh', sizing_mode="stretch_width", height=300)

widget = pn.widgets.RadioButtonGroup.from_param(
    plot_pane.param.backend, color="primary", variant="outline"
)

pn.Column(widget, plot_pane)
```

## Linked Axes

By default the axes of plots with shared key or value dimensions are linked. You can remove the link by setting the `linked_axes` parameter to `False`.

```python
not_linked_plot = df.hvplot.scatter(x="group", y="value", responsive=True, title="Not Linked Axes").opts(active_tools=['box_zoom'])
linked_plot = df.hvplot.scatter(x="group", y="value", responsive=True, title="Linked Axes").opts(active_tools=['box_zoom'])

pn.Column(
    pn.pane.HoloViews(not_linked_plot, backend='bokeh', sizing_mode="stretch_width", height=200, linked_axes=False),
    pn.pane.HoloViews(linked_plot, backend='bokeh', sizing_mode="stretch_width", height=200),
    pn.pane.HoloViews(linked_plot, backend='bokeh', sizing_mode="stretch_width", height=200),
)
```

## Theme

You can change the `theme`.

```python
plot = df.hvplot.scatter(x="group", y="value", height=300, responsive=True)
pn.pane.HoloViews(plot, height=300, theme="night_sky")
```

## Layout and Widget Parameters

Please note that above we used the `Holoviews` pane to display HoloViews objects.

Below we will be using `pn.panel(...)` instead. `pn.panel(...)` is the same as `pn.pane.HoloViews(...).layout`

### Center

You can center your plots via the `center` parameter.

```python
plot = df.hvplot.scatter(x="group", y="value", height=100, width=400)

pn.Column(
    "`center=True`, `sizing_mode='fixed'`",
    pn.panel(plot, center=True, sizing_mode="fixed"),
    "`center=True`, `sizing_mode='stretch_width'`",
    pn.panel(plot, center=True, sizing_mode="stretch_width"),
    "`center=False`, `sizing_mode='fixed'`",
    pn.panel(plot),
    "`center=False`, `sizing_mode='stretch_width'`",
    pn.panel(plot, sizing_mode="stretch_width"),
)
```

### HoloMap and DynamicMap Widgets

[HoloViews](https://holoviews.org/) (the framework) natively renders plots with widgets if a `HoloMap` or [DynamicMap](https://holoviews.org/reference/containers/bokeh/DynamicMap.html) declares any *key dimensions*. This approach efficiently updates just the data inside a plot instead of replacing it entirely.

When rendering a `HoloMap` or `DynamicMap` object with `pn.panel`, then the `pn.pane.HoloViews(...).layout` will be displayed. Not `pn.pane.HoloViews(...)`.

```python
import pandas as pd
import hvplot.pandas
import holoviews.plotting.bokeh

def sine(frequency=1.0, amplitude=1.0, function='sin'):
    xs = np.arange(200)/200*20.0
    ys = amplitude*getattr(np, function)(frequency*xs)
    return pd.DataFrame(dict(y=ys), index=xs).hvplot(height=250, responsive=True)

dmap = hv.DynamicMap(sine, kdims=['frequency', 'amplitude', 'function']).redim.range(
    frequency=(0.1, 10), amplitude=(1, 10)).redim.values(function=['sin', 'cos', 'tan'])

dmap_panel = pn.pane.HoloViews(dmap, height=400, sizing_mode="stretch_width")
dmap_panel
```

Lets inspect the `dmap_panel`

```python
print(dmap_panel)
```

Lets try to modify the `FloatSlider` before we render it:

```python
float_slider = hv_panel[1][0]

float_slider.styles = {'border': '2px solid red', 'padding': '10px', 'border-radius': '5px'}

float_slider
```

Lets try to reorganize the layout

```python
widgets = hv_panel[1]

pn.Row(pn.Column(*widgets), hv_panel[0])
```

The widgets in the `.layout` can be customized via the `widgets`, `widget_location`, `widget_layout` and `widget_type` parameters.

#### `default_widgets`

The mapping between the type of dimension and the widget is given by the `default_widgets`. The mapping supports the following cases:

- `'date'`: For datetime ranges.
- `'discrete'`: For categorical values.
- `'discrete_numeric'`: For discrete, numeric values.
- `'float'`: For continuous floating-point ranges.
- `'int'`: For integer ranges.
- `'scrubber'`: For stepping through frame sequences.

Note that the type may defined as a tuple to offer different widgets for  static case (i.e. a `HoloMap`) and the dynamic case (i.e. a `DynamicMap`).

The type of widget must match the type, i.e. a continuous float or int widget must offer `start` and `end` points and a `discrete` widget must accept `options`.

Here we override the types for the 'discrete', 'float' and 'int' types:

```python
pn.pane.HoloViews(
    dmap, height=400, sizing_mode="stretch_width", default_widgets={
        'discrete': pn.widgets.RadioButtonGroup,
        'float': pn.widgets.NumberInput,
        'int': pn.widgets.NumberInput
    }
)
```

#### `widget_location`

The HoloViews pane offers options to lay out the plot and widgets in a number of preconfigured arrangements using the ``center`` and ``widget_location`` parameters.

The ``widget_location`` parameter accepts all of the following options:

    ['left', 'bottom', 'right', 'top', 'top_left', 'top_right', 'bottom_left',
     'bottom_right', 'left_top', 'left_bottom', 'right_top', 'right_bottom']

```python
pn.panel(dmap, center=True, widget_location='left')
```

#### `widget_layout`

Lets change the widget layout to a `Row`.

```python
pn.panel(dmap, center=True, widget_layout=pn.Row, widget_location='top_left')
```

#### `widgets`

As we saw above, the HoloViews pane will automatically try to generate appropriate widgets for the type of data, usually defaulting to ``DiscreteSlider`` and ``Select`` widgets. This behavior can be modified by providing a dictionary of ``widgets`` by dimension name.  The values of this dictionary can override the default widget in one of three ways:

* Supplying a ``Widget`` instance
* Supplying a compatible ``Widget`` type
* Supplying a dictionary of ``Widget`` parameter overrides

``Widget`` instances will be used as they are supplied and are expected to provide values matching compatible with the values defined on HoloMap/DynamicMap. Similarly if a ``Widget`` type is supplied it should be discrete if the parameter space defines a discrete set of values.  If the defined parameter space is continuous, on the other hand, it may supply any valid value.

In the example below the 'amplitude' dimension is overridden with an explicit ``Widget`` instance, the 'function' dimension is overridden with a RadioButtonGroup letting us toggle between the different functions, and lastly the 'value' parameter on the 'frequency' widget is overridden to change the initial value:

```python
hv_panel = pn.pane.HoloViews(dmap, widgets={
    'amplitude': pn.widgets.LiteralInput(value=1., type=(float, int)),
    'function': pn.widgets.RadioButtonGroup,
    'frequency': {'value': 5}
}).layout

hv_panel
```

### Bound Functions and DynamicMaps

When working with reactive references and functions (such as those returned by `.bind`, `.depends` or `.rx`) that return HoloViews elements and overlays it is recommended that you wrap them in a `DynamicMap`. This allows us to construct plots that depend on the values of widgets or other parameters or expressions in a straightforward way. Note that this differs from auto-generating widgets from dimensions as we've seen so far. Internally HoloViews will inspect the function and create a so called `Stream` that updates the `DynamicMap` when the dependencies change. This also means that any widget you depend on will not appear alongside the other widgets, derived from a dimension.

Instead of re-rendering the entire plot each time a parameter changes this will delegate the update to HoloViews and update the data inplace:

```python
def get_plot(n):
    return hv.Scatter(range(n), kdims="x", vdims="y").opts(
        height=300, responsive=True, xlim=(0, 100), ylim=(0, 100)
    )

widget = pn.widgets.IntSlider(value=50, start=1, end=100, name="Number of points")
plot = hv.DynamicMap(pn.bind(get_plot, widget))

pn.Column(widget, plot)
```

Please note the bound function may not return `Layout`s, `NdLayout`s, `GridSpace`s, `DynamicMap`s or `HoloMaps` as these are not supported by the `DynamicMap`.

---
