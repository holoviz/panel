# Display Activity with Indicators

Show activity with indicators just as rotating blades show the activity of wind turbines:

- Overlay a loading indicator with the `loading` parameter.
- Automatically overlay a loading indicator on output from *bound functions* by setting `loading_indicator=True`.
- Improve the user experience of slowly loading applications by setting `defer_load=True` .
- Customize the loading indication with *loading indicator* components.

:::{note}
In the sections below, we may execute the code directly in the Panel documentation by using the green *run* button, in a notebook cell, or in a file named `app.py` served with `panel serve app.py --autoreload`.
:::

## Overlay a Loading Indicator

We can overlay a loading indicator on a Panel component by setting `loading=True`.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.Button(name="Loading", loading=True, button_type="primary").servable()
```

It also works for composed components

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.WidgetBox(
    pn.widgets.Checkbox(name="Checked", value=True),
    pn.widgets.Button(name="Submit", button_type="primary"),
    loading=True, margin=(10,10),
).servable()
```

## Automatically overlay a Loading Indicator

We can automatically overlay a loading indicator on *bound functions* by setting `loading_indicator=True` in `pn.panel`.

Run the code below

```{pyodide}
import panel as pn
from time import sleep

pn.extension("vega")

button = pn.widgets.Button(name="Submit", button_type="primary")

def get_figure(running):
    if not running:
        return "Click Submit"

    sleep(2)
    return pn.pane.Vega({
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "values": [
            {"Day": "Monday", "Wind Speed (m/s)": 7},
            {"Day": "Tuesday", "Wind Speed (m/s)": 4},
            {"Day": "Wednesday", "Wind Speed (m/s)": 9},
            {"Day": "Thursday", "Wind Speed (m/s)": 4},
            {"Day": "Friday", "Wind Speed (m/s)": 4},
            {"Day": "Saturday", "Wind Speed (m/s)": 5},
            {"Day": "Sunday", "Wind Speed (m/s)": 4}
            ]
        },
        "mark": {"type": "line", "point": True},
        "encoding": {
            "x": {"field": "Day", "type": "ordinal"},
            "y": {"field": "Wind Speed (m/s)", "type": "quantitative", "scale": {"domain": [0, 10]}},
            "tooltip": [{"field": "Day"}, {"field": "Wind Speed (m/s)"}]
        },
        "width": "container",
        "height": "container",
        "title": "Wind Speed Over the Week"
    }, height=400, sizing_mode="stretch_width")

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function, loading_indicator=True)
pn.Column(button, plot, sizing_mode="stretch_width").servable()
```

:::{hint}
You can configure a *global* `loading_indicator` via one of

- `pn.extension(..., loading_indicator=True)`
- `pn.config.loading_indicator=True`.

:::

### Exercise: Configure Global Loading Indicator

Add two more plots to the previous example. Make sure a *loading indicator* is applied to all 3 plots when loading.

:::{dropdown} Solution: 3 Plots with loading indicator

```{pyodide}
import panel as pn
from time import sleep

pn.extension("vega", sizing_mode="stretch_width", loading_indicator=True)

button = pn.widgets.Button(name="Submit", button_type="primary")

def get_figure(running):
    if not running:
        return "Click Submit"

    sleep(2)
    return pn.pane.Vega({
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "values": [
            {"Day": "Monday", "Wind Speed (m/s)": 7},
            {"Day": "Tuesday", "Wind Speed (m/s)": 4},
            {"Day": "Wednesday", "Wind Speed (m/s)": 9},
            {"Day": "Thursday", "Wind Speed (m/s)": 4},
            {"Day": "Friday", "Wind Speed (m/s)": 4},
            {"Day": "Saturday", "Wind Speed (m/s)": 5},
            {"Day": "Sunday", "Wind Speed (m/s)": 4}
            ]
        },
        "mark": {"type": "line", "point": True},
        "encoding": {
            "x": {"field": "Day", "type": "ordinal"},
            "y": {"field": "Wind Speed (m/s)", "type": "quantitative", "scale": {"domain": [0, 10]}},
            "tooltip": [{"field": "Day"}, {"field": "Wind Speed (m/s)"}]
        },
        "width": "container",
        "height": "container",
        "title": "Wind Speed Over the Week"
    }, height=400)

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function)
bound_function2 = pn.bind(get_figure, button)
plot2 = pn.panel(bound_function2)
bound_function3 = pn.bind(get_figure, button)
plot3 = pn.panel(bound_function3)

pn.Column(button, plot, pn.Row(plot2, plot3), sizing_mode="stretch_width").servable()
```

:::

### Exercise: Defer the Load

:::{hint}
If the *bound functions* in the application are slow, it will take a while for the application to *load*.

We can improve the user experience by using `defer_load=True`. This can be used locally in `pn.panel` or globally via `pn.extension(..., defer_load=True)` or `pn.config.defer_load=True`.
:::

Run the code below

```{pyodide}
import panel as pn
from time import sleep

pn.extension("vega", sizing_mode="stretch_width")

button = pn.widgets.Button(name="Submit", button_type="primary")

def get_figure(_):
    sleep(2)
    return pn.pane.Vega({
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "values": [
            {"Day": "Monday", "Wind Speed (m/s)": 7},
            {"Day": "Tuesday", "Wind Speed (m/s)": 4},
            {"Day": "Wednesday", "Wind Speed (m/s)": 9},
            {"Day": "Thursday", "Wind Speed (m/s)": 4},
            {"Day": "Friday", "Wind Speed (m/s)": 4},
            {"Day": "Saturday", "Wind Speed (m/s)": 5},
            {"Day": "Sunday", "Wind Speed (m/s)": 4}
            ]
        },
        "mark": {"type": "line", "point": True},
        "encoding": {
            "x": {"field": "Day", "type": "ordinal"},
            "y": {"field": "Wind Speed (m/s)", "type": "quantitative", "scale": {"domain": [0, 10]}},
            "tooltip": [{"field": "Day"}, {"field": "Wind Speed (m/s)"}]
        },
        "width": "container",
        "height": "container",
        "title": "Wind Speed Over the Week"
    }, height=400)

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function)
bound_function2 = pn.bind(get_figure, button)
plot2 = pn.panel(bound_function2)
bound_function3 = pn.bind(get_figure, button)
plot3 = pn.panel(bound_function3)

pn.Column(button, plot, pn.Row(plot2, plot3), sizing_mode="stretch_width").servable()
```

Notice that it takes +6 seconds before the application loads.

Click the `Submit` button. Notice the *missing* *loading indicator*.

Improve the user experience by *deferring the load* and adding a *loading indicator* to each plot.

:::{dropdown} Solution: Loading Indicator + Defer Load

```{pyodide}
import panel as pn
from time import sleep

pn.extension("vega", sizing_mode="stretch_width", defer_load=True, loading_indicator=True)

button = pn.widgets.Button(name="Submit", button_type="primary")

def get_figure(_):
    sleep(2)
    return pn.pane.Vega({
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "data": {
            "values": [
            {"Day": "Monday", "Wind Speed (m/s)": 7},
            {"Day": "Tuesday", "Wind Speed (m/s)": 4},
            {"Day": "Wednesday", "Wind Speed (m/s)": 9},
            {"Day": "Thursday", "Wind Speed (m/s)": 4},
            {"Day": "Friday", "Wind Speed (m/s)": 4},
            {"Day": "Saturday", "Wind Speed (m/s)": 5},
            {"Day": "Sunday", "Wind Speed (m/s)": 4}
            ]
        },
        "mark": {"type": "line", "point": True},
        "encoding": {
            "x": {"field": "Day", "type": "ordinal"},
            "y": {"field": "Wind Speed (m/s)", "type": "quantitative", "scale": {"domain": [0, 10]}},
            "tooltip": [{"field": "Day"}, {"field": "Wind Speed (m/s)"}]
        },
        "width": "container",
        "height": "container",
        "title": "Wind Speed Over the Week"
    }, height=400)

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function)
bound_function2 = pn.bind(get_figure, button)
plot2 = pn.panel(bound_function2)
bound_function3 = pn.bind(get_figure, button)
plot3 = pn.panel(bound_function3)

pn.Column(button, plot, pn.Row(plot2, plot3), sizing_mode="stretch_width").servable()
```

:::

## Loading Indicators

Panel provides a selection of *loading indicators*. For example the [`LoadingSpinner`](../../reference/indicators/LoadingSpinner.ipynb) and [`Progress`](../../reference/indicators/Progress.ipynb) indicator.

Run the code below

```{pyodide}
import panel as pn

pn.extension()

pn.Row(
    pn.Column(
        "## Loading Spinner",
        pn.Column(
            pn.indicators.LoadingSpinner(value=False, height=25, width=25),
            pn.indicators.LoadingSpinner(
                value=True, height=25, width=25, color="secondary"
            ),
        ),
    ),
    pn.Column(
        "## Progress",
        pn.Column(
            pn.indicators.Progress(
                name="Progress", value=20, width=150, bar_color="dark"
            ),
            pn.indicators.Progress(
                name="Progress", active=True, width=150, bar_color="dark"
            ),
        ),
    )
).servable()
```

### Exercise: Loading Spinner

Run the code below

```{pyodide}
from time import sleep

import panel as pn

pn.extension()

button = pn.widgets.Button(name="Submit", button_type="primary")

running_indicator = pn.indicators.LoadingSpinner(
    value=False, height=25, width=25, color="secondary", visible=True
)


def predict(running):
    if not running:
        return "Click Submit"

    sleep(2)
    return "Its a Wind Turbine!"


prediction = pn.bind(predict, button)

pn.Column(
    button,
    running_indicator,
    prediction,
).servable()
```

Notice the poor user experience.

Now fix the issues

- Only show `LoadingSpinner` when the prediction is running.
- Make the `LoadingSpinner` spin when the prediction is running

:::::{dropdown} Solutions: LoadingSpinner

::::{tab-set}

:::{tab-item} Basic
:sync: basic

```{pyodide}
from time import sleep

import panel as pn

pn.extension()

button = pn.widgets.Button(name="Submit", button_type="primary")

running_indicator = pn.indicators.LoadingSpinner(
    value=False, height=25, width=25, color="secondary", visible=False
)


def predict(running):
    if not running:
        return "Click Submit"

    running_indicator.value = running_indicator.visible = True

    sleep(2)
    running_indicator.value = running_indicator.visible = False
    return "Its a Wind Turbine!"


prediction = pn.bind(predict, button)

pn.Column(button, running_indicator, prediction).servable()
```

:::

:::{tab-item} Reactive Expressions
:sync: reactive-expressions

```{pyodide}
from time import sleep

import panel as pn

pn.extension()

is_running = pn.rx(False)

button = pn.widgets.Button(
    name="Submit", button_type="primary", disabled=is_running, loading=is_running
)

running_indicator = pn.indicators.LoadingSpinner(
    value=is_running, height=25, width=25, color="secondary", visible=is_running
)


def predict(running):

    if not running:
        return "Click Submit"

    is_running.rx.value=True
    sleep(2)
    is_running.rx.value=False
    return "Its a Wind Turbine!"


prediction = pn.bind(predict, button)

pn.Column(button, running_indicator, prediction).servable()
```

:::

::::

:::::

## Recap

We have showed activity with indicators just as rotating blades show the activity of wind turbines:

- Overlay a loading indicator with the `loading` parameter.
- Automatically overlay a loading indicator on output from *bound functions* by setting `loading_indicator=True`.
- Improve the user experience of slowly loading applications by setting `defer_load=True` .
- Customize the loading indication with *loading indicator* components.

## Resources

### How-to

- [Customize Loading Icon](../../how_to/styling/load_icon.md)
- [Migrate from Streamlit | Show Activity](../../how_to/streamlit_migration/activity.md)
- [Defer Load](../../how_to/callbacks/defer_load.md)
