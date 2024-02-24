# Display Activity

Let's bring our Panel apps to life with dynamic indicators and notifications, much like the rotating blades of wind turbines indicate activity.

- Overlay loading indicators using the `loading` parameter.
- Automatically overlay loading indicators on outputs from *bound functions* by enabling `loading_indicator=True`.
- Enhance user experience with slowly loading applications by deferring load with `defer_load=True`.
- Customize loading indicators with various components.
- Provide notifications using `pn.state.notifications`.

:::{note}
In the sections below, you can execute the code directly in the Panel documentation using the green *run* button, in a notebook cell, or in a file named `app.py` served with `panel serve app.py --autoreload`.
:::

```{pyodide}
import panel as pn

pn.extension(notifications=True)
```

## Overlay a Loading Indicator

We can overlay a loading indicator on a Panel component by setting `loading=True`.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.widgets.Button(name="Loading", loading=True, button_type="primary").servable()
```

It also works for composed components.

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

## Automatically Overlay a Loading Indicator

We can automatically overlay a loading indicator on *bound functions* by setting `loading_indicator=True` in `pn.panel`.

Run the code below:

```{pyodide}
from time import sleep
import hvplot.pandas
import pandas as pd
import panel as pn

pn.extension()

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

button = pn.widgets.Button(name="Submit", button_type="primary")

def get_figure(running):
    if not running:
        return "Click Submit"

    sleep(2)
    return data.hvplot(x="Day", y="Wind Speed (m/s)", line_width=10, ylim=(0,10), title="Wind Speed")

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function, height=400, sizing_mode="stretch_width", loading_indicator=True)

pn.Column(button, plot).servable()
```

### Exercise: Configure Global Loading Indicator

Add two more plots to the previous example. Make sure a loading indicator is applied to all three plots when loading.

:::{hint}
You can configure a global `loading_indicator` via one of:

- `pn.extension(..., loading_indicator=True)`
- `pn.config.loading_indicator=True`.

:::

:::{dropdown} Solution

```{pyodide}
from time import sleep
import hvplot.pandas
import pandas as pd
import panel as pn

pn.extension(sizing_mode="stretch_width", loading_indicator=True)

button = pn.widgets.Button(name="Submit", button_type="primary")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

def get_figure(running):
    if not running:
        return None

    sleep(2)
    return data.hvplot(x="Day", y="Wind Speed (m/s)", line_width=10, ylim=(0,10), title="Wind Speed")

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function, height=400)
bound_function2 = pn.bind(get_figure, button)
plot2 = pn.panel(bound_function2, height=400)
bound_function3 = pn.bind(get_figure, button)
plot3 = pn.panel(bound_function3, height=400)

pn.Column(button, plot, pn.Row(plot2, plot3), sizing_mode="stretch_width").servable()
```

:::

### Exercise: Defer the Load

:::{hint}
If the bound functions in the application are slow, it will take a while for the application to load.

We can improve the user experience by using `defer_load=True`. This can be used locally in `pn.panel` or globally via `pn.extension(..., defer_load=True)` or `pn.config.defer_load=True`.
:::

Run the code below

```{pyodide}
from time import sleep
import hvplot.pandas
import pandas as pd
import panel as pn

pn.extension(sizing_mode="stretch_width")

button = pn.widgets.Button(name="Submit", button_type="primary")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

def get_figure(running):
    sleep(2)
    return data.hvplot(x="Day", y="Wind Speed (m/s)", line_width=10, ylim=(0,10), title="Wind Speed")

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function, height=400)
bound_function2 = pn.bind(get_figure, button)
plot2 = pn.panel(bound_function2, height=400)
bound_function3 = pn.bind(get_figure, button)
plot3 = pn.panel(bound_function3, height=400)

pn.Column(button, plot, pn.Row(plot2, plot3), sizing_mode="stretch_width").servable()
```

Notice that it takes +6 seconds before the application loads.

Click the `Submit` button. Notice the missing loading indicator.

Improve the user experience by deferring the load and adding a loading indicator to each plot.

:::{dropdown} Solution

```{pyodide}
from time import sleep
import hvplot.pandas
import pandas as pd
import panel as pn

pn.extension(sizing_mode="stretch_width", defer_load=True, loading_indicator=True)

button = pn.widgets.Button(name="Submit", button_type="primary")

data = pd.DataFrame([
    ('Monday', 7), ('Tuesday', 4), ('Wednesday', 9), ('Thursday', 4),
    ('Friday', 4), ('Saturday', 5), ('Sunday', 4)], columns=['Day', 'Wind Speed (m/s)']
)

def get_figure(running):
    sleep(2)
    return data.hvplot(x="Day", y="Wind Speed (m/s)", line_width=10, ylim=(0,10), title="Wind Speed")

bound_function = pn.bind(get_figure, button)
plot = pn.panel(bound_function, height=400)
bound_function2 = pn.bind(get_figure, button)
plot2 = pn.panel(bound_function2, height=400)
bound_function3 = pn.bind(get_figure, button)
plot3 = pn.panel(bound_function3, height=400)

pn.Column(button, plot, pn.Row(plot2, plot3), sizing_mode="stretch_width").servable()
```

:::

## Loading Indicators

Panel provides a selection of loading indicators, such as the [`LoadingSpinner`](../../reference/indicators/LoadingSpinner.ipynb) and [`Progress`](../../reference/indicators/Progress.ipynb) indicator.

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
    return "It's a Wind Turbine!"


prediction = pn.bind(predict, button)

pn.Column(
    button,
    running_indicator,
    prediction,
).servable()
```

Notice the poor user experience.

Now fix the issues:

- Show `LoadingSpinner` only when the prediction is running.
- Make the `LoadingSpinner` spin when the prediction is running.

::::{dropdown} Solutions

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
    return "It's a Wind Turbine!"


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
    return "It's a Wind Turbine!"


prediction = pn.bind(predict, button)

pn.Column(button, running_indicator, prediction).servable()
```

:::

::::

:::::

## Notifications

Let's display an `info` notification.

```{pyodide}
import panel as pn

pn.extension(notifications=True)

def send_notification(event):
    pn.state.notifications.info("This is a notification", duration=3000)

pn.widgets.Button(name="Send", on_click=send_notification).servable()
```

Try clicking the `Button`. You should see a notification pop up in the lower left corner of the app.

:::{note}
The code refers to:

- `pn.extension(notifications=True)`: We need to set `notifications=True` to support notifications in Panel.
- `pn.state.notifications.info(..., duration=3000)`: We send an `info` notification. The notification is shown for `3000` milliseconds.
:::

Try changing `pn.state.notifications.info` to `pn.state.notifications.warning`. Then click the `Button`. What happens?

Try changing `duration=3000` to `duration=0`. Then click the `Button`. What happens?

See the [Notifications](../../reference/global/Notifications.ipynb) reference guide for more detail.

## Recap

We've explored how to show activity with indicators, much like the rotating blades of wind turbines:

- Overlay a loading indicator with the `loading` parameter.
- Automatically overlay a loading indicator on output from *bound functions* by setting `loading_indicator=True`.
- Improve the user experience of slowly loading applications by setting `defer_load=True`.
- Customize the loading indication with various components.
- Provide notifications using `pn.state.notifications`.

## Resources

### How-to

- [Customize Loading Icon](../../how_to/styling/load_icon.md)
- [Migrate from Streamlit | Show Activity](../../how_to/streamlit_migration/activity.md)
- [Defer Load](../../how_to/callbacks/defer_load.md)

### Reference Guides

- [Notifications](../../reference/global/Notifications.ipynb)
