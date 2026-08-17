# Plotly
---
The Plotly pane displays [Plotly plots](https://plotly.com/python/) within a Panel application. It enhances the speed of plot updates by using binary serialization for array data contained in the Plotly object.

It uses [plotly.js](https://plotly.com/javascript/) **version {{PLOTLY_VERSION}}**

Please remember that to use the Plotly pane in a Jupyter notebook, you must activate the [Panel extension](https://panel.holoviz.org/api/cheatsheet.html#pn-extension) and include `"plotly"` as an argument. This step ensures that plotly.js is properly set up.

```python
import panel as pn

pn.extension("plotly")
```

## Parameters:

For details on other options for customizing the component see the general [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides as well as the specific [Style Plotly Plots](../../how_to/styling/plotly.md) how-to guide.

### Core

* **``object``** (object): The Plotly `Figure` or dictionary object being displayed.
* **``config``** (dict): Additional configuration of the plot. See [Plotly configuration options](https://plotly.com/javascript/configuration-options/).

### Update in Place

* **``link_figure``** (bool, default: True): Update the displayed Plotly figure when the Plotly `Figure` is modified in place.

### Events

* **``click_data``** (dict): Click event data from `plotly_click` event.
* **``clickannotation_data``** (dict): Clickannotation event data from `plotly_clickannotation` event.
* **``hover_data``** (dict): Hover event data from `plotly_hover` and `plotly_unhover` events.
* **``relayout_data``** (dict): Relayout event data from `plotly_relayout` event
* **``restyle_data``** (dict): Restyle event data from `plotly_restyle` event
* **``selected_data``** (dict): Selected event data from `plotly_selected` and `plotly_deselect` events.
* **``viewport``** (dict): Current viewport state, i.e. the x- and y-axis limits of the displayed plot. Updated on `plotly_relayout`, `plotly_relayouting` and `plotly_restyle` events.
* **``viewport_update_policy``** (str, default = 'mouseup'): Policy by which the viewport parameter is updated during user interactions
    * ``mouseup``: updates are synchronized when mouse button is released after panning
    * ``continuous``: updates are synchronized continually while panning
    * ``throttle``: updates are synchronized while panning, at intervals determined by the viewport_update_throttle parameter
* **``viewport_update_throttle``** (int, default = 200, bounds = (0, None)): Time interval in milliseconds at which viewport updates are synchronized when viewport_update_policy is "throttle".

___

As with most other types ``Panel`` will automatically convert a Plotly `Figure` to a `Plotly` pane if it is passed to the `pn.panel` function or a Panel layout, but a `Plotly` pane can also be constructed directly using the `pn.pane.Plotly` constructor:

## Basic Example

Lets create a basic example

```python
import numpy as np
import plotly.graph_objs as go

import panel as pn

pn.extension("plotly")

xx = np.linspace(-3.5, 3.5, 100)
yy = np.linspace(-3.5, 3.5, 100)
x, y = np.meshgrid(xx, yy)
z = np.exp(-((x - 1) ** 2) - y**2) - (x**3 + y**4 - x / 5) * np.exp(-(x**2 + y**2))

surface=go.Surface(z=z)
fig = go.Figure(data=[surface])

fig.update_layout(
    title="Plotly 3D Plot",
    width=500,
    height=500,
    margin=dict(t=50, b=50, r=50, l=50),
)

plotly_pane = pn.pane.Plotly(fig)
plotly_pane
```

Once created `Plotly` pane can be updated by assigning a new figure object

```python
new_fig = go.Figure(data=[go.Surface(z=np.sin(z+1))])
new_fig.update_layout(
    title="Plotly 3D Plot",
    width=500,
    height=500,
    margin=dict(t=50, b=50, r=50, l=50),
)

plotly_pane.object = new_fig
```

Lets reset the Plotly pane

```python
plotly_pane.object = fig
```

## Layout Example

The `Plotly` pane supports layouts and subplots of arbitrary complexity, allowing even deeply nested Plotly figures to be displayed:

```python
import panel as pn
from plotly import subplots

pn.extension("plotly")

heatmap = go.Heatmap(
    z=[[1, 20, 30],
       [20, 1, 60],
       [30, 60, 1]],
    showscale=False)

y0 = np.random.randn(50)
y1 = np.random.randn(50)+1

box_1 = go.Box(y=y0)
box_2 = go.Box(y=y1)
data = [heatmap, box_1, box_2]

fig_layout = subplots.make_subplots(
    rows=2, cols=2, specs=[[{}, {}], [{'colspan': 2}, None]],
    subplot_titles=('First Subplot','Second Subplot', 'Third Subplot')
)

fig_layout.append_trace(box_1, 1, 1)
fig_layout.append_trace(box_2, 1, 2)
fig_layout.append_trace(heatmap, 2, 1)

fig_layout['layout'].update(height=600, width=600, title='i <3 subplots')

pn.pane.Plotly(fig_layout)
```

## Responsive Plots

Plotly plots can be made responsive using the `autosize` option on a Plotly layout and a responsive `sizing_mode` argument to the `Plotly` pane:

```python
import pandas as pd
import panel as pn
import plotly.express as px

pn.extension("plotly")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 4), ('Sunday', 4)], columns=['Day', 'Orders']
)

fig_responsive = px.line(data, x="Day", y="Orders")
fig_responsive.update_traces(mode="lines+markers", marker=dict(size=10), line=dict(width=4))
fig_responsive.layout.autosize = True

responsive = pn.pane.Plotly(fig_responsive, height=300)

pn.Column('## A responsive plot', responsive, sizing_mode='stretch_width')
```

## Plot Configuration

You can set the [Plotly configuration options](https://plotly.com/javascript/configuration-options/) via the `config` parameter. Lets try to configure `scrollZoom`:

```python
fig_responsive.update_xaxes(automargin=False)

responsive_with_zoom = pn.pane.Plotly(fig_responsive, config={"scrollZoom": True}, height=300)

pn.Column('## A responsive and scroll zoomable plot', responsive_with_zoom, sizing_mode='stretch_width')
```

Try scrolling with the mouse over the plot!

## Patching

Instead of updating the entire Figure you can efficiently patch traces or the layout if you use a dictionary instead of a Plotly Figure.

Note patching will only be efficient if the ``Figure`` is defined as a dictionary, since Plotly will make copies of the traces, which means that modifying them in place has no effect. Modifying an array will send just the array using a binary protocol, leading to fast and efficient updates.

```python
import numpy as np
import plotly.graph_objs as go

import panel as pn

pn.extension("plotly")

xx = np.linspace(-3.5, 3.5, 100)
yy = np.linspace(-3.5, 3.5, 100)
x, y = np.meshgrid(xx, yy)
z = np.exp(-((x - 1) ** 2) - y**2) - (x**3 + y**4 - x / 5) * np.exp(-(x**2 + y**2))

surface = go.Surface(z=z)
layout = go.Layout(
    title='Plotly 3D Plot',
    autosize=False,
    width=500,
    height=500,
    margin=dict(t=50, b=50, r=50, l=50)
)

fig_patch = dict(data=[surface], layout=layout)

plotly_pane_patch = pn.pane.Plotly(fig_patch)
plotly_pane_patch
```

```python
surface.z = np.sin(z+1)
plotly_pane_patch.object = fig_patch
```

Similarly, modifying the plot ``layout`` will only modify the layout, leaving the traces unaffected.

```python
fig_patch['layout']['width'] = 800

plotly_pane_patch.object = fig_patch
```

Lets reset the Plotly pane

```python
surface.z = z
fig_patch['layout']['width'] = 500

plotly_pane_patch.object = fig_patch
```

## Streaming

You can stream updates by replacing the entire Figure object. To stream efficiently though you should use patching technique described above.

You can stream periodically using `pn.state.add_periodic_callback`.

```python
import pandas as pd
import plotly.graph_objects as go

import panel as pn

pn.extension("plotly")

df_ohlc = pn.cache(pd.read_csv)(
    "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
)

start_index = 50

stream_data = go.Ohlc(
    x=df_ohlc.loc[:start_index, "Date"],
    open=df_ohlc.loc[:start_index, "AAPL.Open"],
    high=df_ohlc.loc[:start_index, "AAPL.High"],
    low=df_ohlc.loc[:start_index, "AAPL.Low"],
    close=df_ohlc.loc[:start_index, "AAPL.Close"],
)

fig_stream = {"data": stream_data, "layout": go.Layout(xaxis_rangeslider_visible=False)}

plotly_pane_stream = pn.pane.Plotly(fig_stream)

def stream():
    index = len(stream_data.x)
    if index == len(df_ohlc):
        index = 0

    stream_data["x"] = df_ohlc.loc[:index, "Date"]
    stream_data["open"] = df_ohlc.loc[:index, "AAPL.Open"]
    stream_data["high"] = df_ohlc.loc[:index, "AAPL.High"]
    stream_data["low"] = df_ohlc.loc[:index, "AAPL.Low"]
    stream_data["close"] = df_ohlc.loc[:index, "AAPL.Close"]
    plotly_pane_stream.object = fig_stream

pn.state.add_periodic_callback(stream, period=100, count=50)

plotly_pane_stream
```

You can also stream via a generator or async generator function:

```python
from asyncio import sleep

import pandas as pd
import plotly.graph_objects as go

import panel as pn

pn.extension("plotly")

df_ohlc = pn.cache(pd.read_csv)(
    "https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv"
)

start_index = 50

gen_data = go.Ohlc(
    x=df_ohlc.loc[:start_index, "Date"],
    open=df_ohlc.loc[:start_index, "AAPL.Open"],
    high=df_ohlc.loc[:start_index, "AAPL.High"],
    low=df_ohlc.loc[:start_index, "AAPL.Low"],
    close=df_ohlc.loc[:start_index, "AAPL.Close"],
)
layout = go.Layout(xaxis_rangeslider_visible=False)

async def stream_generator():
    for _ in range(start_index, start_index+50):
        index = len(gen_data.x)
        if index == len(df_ohlc):
            index = 0

        gen_data["x"] = df_ohlc.loc[:index, "Date"]
        gen_data["open"] = df_ohlc.loc[:index, "AAPL.Open"]
        gen_data["high"] = df_ohlc.loc[:index, "AAPL.High"]
        gen_data["low"] = df_ohlc.loc[:index, "AAPL.Low"]
        gen_data["close"] = df_ohlc.loc[:index, "AAPL.Close"]
        
        yield  {"data": gen_data, "layout": layout}
        await sleep(0.05)

pn.pane.Plotly(stream_generator)
```

## Update in Place

An alternative to updating the figure dictionary is updating the Plotly `Figure` in place, i.e. via its attributes and methods.

```python
import plotly.graph_objects as go

import panel as pn

pn.extension("plotly")

fig_in_place = go.Figure()

button = pn.widgets.Button(label="Create", color="primary")

def handle_click(clicks):
    mod = clicks % 3
    if mod == 1:
        button.name = "Update"
        fig_in_place.add_scatter(y=[2, 1, 4, 3])
        fig_in_place.add_bar(y=[2, 1, 4, 3])
        fig_in_place.layout.title = "New Figure"
    elif mod == 2:
        button.name = "Reset"
        scatter = fig_in_place.data[0]
        scatter.y = [3, 1, 4, 3]
        bar = fig_in_place.data[1]
        bar.y = [5, 3, 2, 8]
        fig_in_place.layout.title.text = "Updated Figure"
    else:
        fig_in_place.data = []
        fig_in_place.layout = {"title": ""}
        button.name = "Create"

pn.bind(handle_click, button.param.clicks, watch=True)
button.clicks=1

plotly_pane_in_place = pn.pane.Plotly(
    fig_in_place,
    height=400,
    width=700,
    # link_figure=False
)

pn.Column(
    button,
    plotly_pane_in_place,
)
```

This enables you to use the Plotly `Figure` in the same way as you would have been using the Plotly `FigureWidget`.

If you for some reason want to disable in place updates, you can set `link_figure=False` when you create the `Plotly` pane. You cannot change this when the pane has been created.

## Events

The Plotly pane enables you to bind to most of the click, hover, selection and other events described in [Plotly Event Handlers](https://plotly.com/javascript/plotlyjs-events/).

### Simple Event Example

```python
import plotly.express as px
import panel as pn
import pandas as pd

pn.extension("plotly")

# Create dataframe
x = [1, 2, 3, 4, 5]
y = [10, 20, 30, 20, 10]
df = pd.DataFrame({'x': x, 'y': y})

# Create scatter plot
fig_events = px.scatter(df, x='x', y='y', title='Click on a Point!', hover_name='x',)
fig_events.update_traces(marker=dict(size=20))
fig_events.update_layout(autosize=True, hovermode='closest')

plotly_pane_event=pn.pane.Plotly(fig_events, height=400, max_width=1200, sizing_mode="stretch_width")

# Define Child View
def child_view(event):
    if not event:
        return "No point clicked"
    try:
        point = event["points"][0]
        index = point['pointIndex']
        x = point['x']
        y = point['y']
    except Exception as ex:
        return f"You clicked the Plotly Chart! I could not determine the point: {ex}"
    
    return f"**You clicked point {index} at ({x}, {y}) on the Plotly Chart!**"

ichild_view = pn.bind(child_view, plotly_pane_event.param.click_data)

# Put things together
pn.Column(plotly_pane_event, ichild_view)
```

### Event Inspection

The be able to work with the events its a good idea to inspect them. You can do that by printing them or including them in your visualization.

Lets display them.

```python
event_parameters = ["click_data", "click_annotation_data", "hover_data", "relayout_data", "restyle_data", "selected_data", "viewport"]

pn.Param(plotly_pane_event, parameters=event_parameters, max_width=1100, name="Plotly Event Parameters")
```

In the plot above, try hovering, clicking, selecting and changing the viewport by panning. Watch how the parameter values just above changes.

### Parent-Child Views

A common technique for exploring higher-dimensional datasets is the use of Parent-Child views. This approach allows you to employ a top-down method to initially exing thehree most important dimensions in the parent plot. You can then select a subset of the data points and examine them in greater detail and across additional dimensions.

Let's create a plot where Box or Lasso selections in the parent plot update a child plot. We will also customize the action bars using the `config` parameter.

```python
import pandas as pd
import plotly.express as px

import panel as pn

pn.extension("plotly")
df = (
    pd.read_csv("https://datasets.holoviz.org/penguins/v1/penguins.csv")
    .dropna()
    .reset_index(drop=True)
)
df["index"] = df.index # Used to filter rows for child view

color_map = {"Adelie": "blue", "Chinstrap": "red", "Gentoo": "green"}

fig_parent = px.scatter(
    df,
    x="flipper_length_mm",
    y="body_mass_g",
    color_discrete_map=color_map,
    custom_data="index",  # Used to filter rows for child view
    color="species",
    title="<b>Parent Plot</b>: Box or Lasso Select Points",
)

def fig_child(selectedData):
    if selectedData:
        indices = [point["customdata"][0] for point in selectedData["points"]]
        filtered_df = df.iloc[indices]
        title = f"<b>Child Plot</b>: Selected Points({len(indices)})"
    else:
        filtered_df = df
        title = f"<b>Child Plot</b>: All Points ({len(filtered_df)})"

    fig = px.scatter(
        filtered_df,
        x="bill_length_mm",
        y="bill_depth_mm",
        color_discrete_map=color_map,
        color="species",
        hover_data={"flipper_length_mm": True, "body_mass_g": True},
        title=title,
    )
    return fig

parent_config = {
    "modeBarButtonsToAdd": ["select2d", "lasso2d"],
    "modeBarButtonsToRemove": [
        "zoomIn2d",
        "zoomOut2d",
        "pan2d",
        "zoom2d",
        "autoScale2d",
    ],
    "displayModeBar": True,
    "displaylogo": False,
}
parent_pane = pn.pane.Plotly(fig_parent, config=parent_config)

ifig_child = pn.bind(fig_child, parent_pane.param.selected_data)
child_config = {
    "modeBarButtonsToRemove": [
        "select2d",
        "lasso2d",
        "zoomIn2d",
        "zoomOut2d",
        "pan2d",
        "zoom2d",
        "autoScale2d",
    ],
    "displayModeBar": True,
    "displaylogo": False,
}
child_pane = pn.pane.Plotly(ifig_child, config=child_config)

pn.FlexBox(parent_pane, child_pane)
```

## Controls

The `Plotly` pane exposes a number of options which can be changed from both Python and Javascript try out the effect of these parameters interactively:

```python
pn.Row(responsive.controls(jslink=True), responsive)
```

---
