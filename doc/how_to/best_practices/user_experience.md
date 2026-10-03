# User Experience

```{pyodide}
import time
import random

import param
import pandas as pd
import panel as pn

pn.extension()
```

The best practices described on this page serve as a checklist of items to keep in mind as you are developing your application. They include items we see users frequently get confused about or things that are easily missed but can make a big difference to the user experience of your application(s).

:::{note}
- Good: recommended, works.
- Okay: works (with intended behavior), potentially inefficient.
- Bad: Deprecated (may or may not work), just don't do it.
- Wrong: Not intended behavior, won't really work.
:::

## Update params effectively

### Good

Use `obj.param.update`:

- to update multiple parameters on an object simultaneously
- as a context manager to temporarily set values, restoring original values on completion

```{pyodide}
def run(event):
    with progress.param.update(
        bar_color="primary",
        active=True,
    ):
        for i in range(0, 101):
            time.sleep(0.01)
            progress.value = i

button = pn.ui.Button(label="Run", on_click=run)
progress = pn.indicators.Progress(value=100, active=False, bar_color="dark")
pn.ui.Row(button, progress)
```

### Okay

The following shows setting parameters individually, which could be inefficient and may temporarily leave the object in an inconsistent state.

```{pyodide}
def run(event):
    try:
        progress.bar_color = "primary"
        progress.active = True
        for i in range(0, 101):
            time.sleep(0.01)
            progress.value = i
    finally:
        progress.bar_color = "dark"
        progress.active = False

button = pn.ui.Button(label="Run", on_click=run)
progress = pn.indicators.Progress(value=100, active=False, bar_color="dark")
pn.ui.Row(button, progress)
```

## Throttle slider callbacks

### Good

When callbacks are expensive to run, you can prevent sliders from triggering too many callbacks, by setting `throttled=True`. When throttled, callbacks will be triggered only once, upon mouse-up.

```{pyodide}
pn.extension(throttled=True)

def callback(value):
    time.sleep(2)
    return f"# {value}"

slider = pn.ui.IntSlider(end=10)
output = pn.bind(callback, slider)
pn.ui.Row(slider, output)
```

### Good

Alternatively, you can apply throttling only to the specific widgets with the most expensive callbacks, by binding to `value_throttled` instead of `value`.

```{pyodide}
def callback(value):
    time.sleep(2)
    return f"# {value}"

slider = pn.ui.IntSlider(end=10)
output = pn.bind(callback, slider.param.value_throttled)
pn.ui.Row(slider, output)
```

### Bad

Binding against `value` can be really slow for expensive callbacks.

```{pyodide}
def callback(value):
    time.sleep(2)
    return f"# {value}"

slider = pn.ui.IntSlider(end=10)
output = pn.bind(callback, slider.param.value)
pn.ui.Row(slider, output)
```

## Defer expensive operations

### Good

It's easy to defer the execution of all bound and displayed functions with `pn.extension(defer_load=True)` (note this applies to served applications, not to interactive notebook environments):

```{pyodide}
pn.extension(defer_load=True, loading_indicator=True)

def onload():
    time.sleep(5)  # simulate expensive operations
    return pn.ui.Column(
        "Welcome to this app!",
    )

layout = pn.ui.Column("Check this out!", onload)
# layout.show()
```

### Okay

If you need finer control, start by instantiating the initial layout with placeholder `pn.Columns`, then populate it later in `onload`.

```{pyodide}
import time

def onload():
    time.sleep(1)  # simulate expensive operations
    layout[:] = ["Welcome to this app!"]

layout = pn.ui.Column("Loading...")
display(layout)
pn.state.onload(onload)
```

## Show indicator while computing

### Good

Set `loading=pn.state.param.busy` to overlay a spinner while processing to let the user know it's working.

```{pyodide}
def process_load(event):
    time.sleep(3)

button = pn.ui.Button(label="Click me", on_click=process_load)
widget_box = pn.ui.WidgetBox(button, loading=pn.state.param.busy, height=300, width=300)
widget_box
```

### Good

Set `loading=True` to show a spinner while processing to let the user know it's working.

```{pyodide}
def compute(event):
    with layout.param.update(loading=True):
        time.sleep(3)
        layout.append("Computation complete!")

button = pn.ui.Button(label="Compute", on_click=compute)
layout = pn.ui.Column("Click below to compute", button)

layout
```

### Okay

You can also wrap a `try/finally` to do the same thing.

```{pyodide}
def compute(event):
    try:
        layout.loading = True
        time.sleep(3)
        layout.append("Computation complete!")
    finally:
        layout.loading = False

button = pn.ui.Button(label="Compute", on_click=compute)
layout = pn.ui.Column("Click below to compute", button)

layout
```

## Manage exceptions gracefully

### Good

Use:
- `try` block to update values on success
- `except` block to update values on exception
- `finally` block to update values regardless

```{pyodide}
def compute(divisor):
    try:
        busy.value = True
        time.sleep(1)
        output = 1 / divisor
        text.value = "Success!"
    except Exception as exc:
        output = "Undefined"
        text.value = f"Error: {exc}"
    finally:
        busy.value = False
    return f"Output: {output}"

busy = pn.ui.LoadingSpinner(width=10, height=10)
text = pn.ui.StaticText()

slider = pn.ui.IntSlider(label="Divisor")
output = pn.bind(compute, slider)

layout = pn.ui.Column(pn.ui.Row(busy, text), slider, output)
layout
```

## Cache values for speed

### Good

Wrap your callback with a `pn.cache` decorator so that values are automatically cached so that expensive computations are not repeated.

```{pyodide}
@pn.cache
def callback(value):
    time.sleep(2)
    return f"# {value}"

slider = pn.ui.IntSlider(end=3)
output = pn.bind(callback, slider.param.value_throttled)
pn.ui.Row(slider, output)
```

### Okay

Or, manually handle the cache yourself with `pn.state.cache`.

```{pyodide}
def callback(value):
    output = pn.state.cache.get(value)
    if output is None:
        time.sleep(2)
        output = f"# {value}"
        pn.state.cache[value] = output
    return output

slider = pn.ui.IntSlider(end=3)
output = pn.bind(callback, slider.param.value_throttled)
pn.ui.Row(slider, output)
```

## Preserve axes ranges on update

### Good

When you are working with HoloViews or hvPlot in Panel, you can prevent the plot from resetting to its original axes ranges when zoomed in by wrapping it with `hv.DynamicMap`.

```{pyodide}
import numpy as np
import holoviews as hv
hv.extension("bokeh")

data = []

def add_point(clicks):
    data.append((np.random.random(), (np.random.random())))
    return hv.Scatter(data)

button = pn.ui.Button(label="Add point")
plot = hv.DynamicMap(pn.bind(add_point, button.param.clicks))
pn.ui.Column(button, plot)
```

### Okay

If you want the object to be completely refreshed, simply drop `hv.DynamicMap`. If it's a long computation, it's good to set `loading_indicator=True`.

```{pyodide}
import numpy as np
import holoviews as hv
hv.extension("bokeh")
pn.extension(defer_load=True, loading_indicator=True)

data = []

def add_point(clicks):
    data.append((np.random.random(), (np.random.random())))
    return hv.Scatter(data)

button = pn.ui.Button(label="Add point")
plot = pn.bind(add_point, button.param.clicks)
pn.ui.Column(button, plot)
```

## FlexBox instead of Column/Row

### Good

`pn.ui.FlexBox` automatically moves objects to another row/column, depending on the space available.

```{pyodide}
rcolor = lambda: "#%06x" % random.randint(0, 0xFFFFFF)

pn.ui.FlexBox(
    pn.ui.HTML(str(5), styles=dict(background=rcolor()), width=1000, height=100),
    pn.ui.HTML(str(5), styles=dict(background=rcolor()), width=1000, height=100)
)
```

### Okay

`pn.ui.Column`/`pn.ui.Row` will overflow if the content is too long/wide.

```{pyodide}
rcolor = lambda: "#%06x" % random.randint(0, 0xFFFFFF)

pn.ui.Row(
    pn.ui.HTML(str(5), styles=dict(background=rcolor()), width=1000, height=100),
    pn.ui.HTML(str(5), styles=dict(background=rcolor()), width=1000, height=100)
)
```

## Reuse objects for efficiency

### Good

Imagine Panel components as placeholders and use them as such, rather than re-creating them on update.

```{pyodide}
def randomize(event):
    df_pane.object = pd.DataFrame(np.random.randn(10, 3), columns=list("ABC"))

button = pn.ui.Button(label="Compute", on_click=randomize)
df_pane = pn.ui.DataFrame()
button.param.trigger("clicks")  # initialize

pn.ui.Column(button, df_pane)
```

### Okay

If your callback returns a Panel object rather than the underlying object being displayed, you'll end up instantiating the `pn.ui.DataFrame` on every click (which is typically slower and will often have distracting flickering).

```{pyodide}
def randomize(clicks):
    return pn.ui.DataFrame(pd.DataFrame(np.random.randn(10, 3), columns=list("ABC")))

button = pn.ui.Button(label="Compute")
df_pane = pn.bind(randomize, button.param.clicks)
button.param.trigger("clicks")  # initialize

pn.ui.Column(button, df_pane)
```
