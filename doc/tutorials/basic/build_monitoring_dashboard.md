# Build a Monitoring Dashboard

In this tutorial, we will construct a *display-only* dashboard that refreshes the entire page periodically.

These types of dashboards are suitable for displaying on a large screen running continuously, such as in a call center, control room, or trading area.

![Monitoring Dashboard](https://assets.holoviz.org/panel/tutorials/build-monitoring-dashboard.gif)

:::::{dropdown} Dependencies

```bash
panel scipy
```

:::::

:::::{dropdown} Code

```python
import numpy as np
import panel as pn
from scipy.interpolate import interp1d

pn.extension()

ACCENT = "teal"

WIND_SPEED_STD_DEV = 2.0
WIND_SPEED_MEAN = 8.0

WIND_SPEEDS = np.array([0, 3, 6, 9, 12, 15, 18, 21])  # Wind speed (m/s)
POWER_OUTPUTS = np.array([0, 39, 260, 780, 1300, 1300, 0, 0])  # Power output (MW)

# Extract Data

def get_wind_speed():
    # Replace with your wind speed source
    return round(np.random.normal(WIND_SPEED_MEAN, WIND_SPEED_STD_DEV), 1)

wind_speed = get_wind_speed()

# Transform Data

def get_power_output(wind_speed):
    # Replace with your power output calculation
    power_interpolation = interp1d(
        WIND_SPEEDS, POWER_OUTPUTS, kind="linear", fill_value="extrapolate"
    )
    return np.round(power_interpolation(wind_speed), 1)

power_output = get_power_output(wind_speed)

# View Data

wind_speed_view = pn.indicators.Number(
    name="Wind Speed",
    value=wind_speed,
    format="{value} m/s",
    colors=[(10, ACCENT), (100, "red")],
)
power_output_view = pn.indicators.Number(
    name="Power Output",
    value=power_output,
    format="{value} MW",
    colors=[
        (power_output, ACCENT),
        (max(POWER_OUTPUTS), "red"),
    ],
)
indicators = pn.FlexBox(wind_speed_view, power_output_view)

# Layout and style with template

pn.template.FastListTemplate(
    title="WTG Monitoring Dashboard",
    main=[indicators],
    accent=ACCENT,
    main_layout=None,
    theme="dark",
    theme_toggle=False,
    meta_refresh="2",  # Automatically refresh every 2 seconds
).servable();  # The ; is only needed if used in a notebook
```

:::::

## Install the dependencies

Please ensure that [Panel](https://panel.holoviz.org) and [SciPy](https://scipy.org/) are installed.

::::{tab-set}

:::{tab-item} conda
:sync: conda

```bash
conda install -y -c conda-forge panel scipy
```

:::

:::{tab-item} pip
:sync: pip

```bash
pip install panel scipy
```

:::

::::

## Explanation

Let's dissect the code that brings our dashboard to life:

```{pyodide}
import numpy as np
import panel as pn
from scipy.interpolate import interp1d
```

We import the necessary libraries: [NumPy](https://numpy.org/) for numerical computations, [Panel](https://panel.holoviz.org) for building interactive web apps, and [SciPy](https://scipy.org/) for interpolation.

```{pyodide}
pn.extension()
```

We load the JavaScript dependencies required by our app.

```{pyodide}
ACCENT = "teal"

WIND_SPEED_STD_DEV = 2.0
WIND_SPEED_MEAN = 8.0

WIND_SPEEDS = np.array([0, 3, 6, 9, 12, 15, 18, 21])  # Wind speed (m/s)
POWER_OUTPUTS = np.array([0, 39, 260, 780, 1300, 1300, 0, 0])  # Power output (MW)
```

We set some constants related to wind speed and power output data.

```{pyodide}
def get_wind_speed():
    return round(np.random.normal(WIND_SPEED_MEAN, WIND_SPEED_STD_DEV), 1)

wind_speed = get_wind_speed()
```

A function `get_wind_speed()` generates a random wind speed value based on a normal distribution.

```{pyodide}
def get_power_output(wind_speed):
    power_interpolation = interp1d(
        WIND_SPEEDS, POWER_OUTPUTS, kind="linear", fill_value="extrapolate"
    )
    return np.round(power_interpolation(wind_speed), 1)

power_output = get_power_output(wind_speed)
```

Another function `get_power_output(wind_speed)` calculates the corresponding power output based on the provided wind speed using linear interpolation.

```{pyodide}
wind_speed_view = pn.indicators.Number(
    name="Wind Speed",
    value=wind_speed,
    format="{value} m/s",
    colors=[(10, ACCENT), (100, "red")],
)
power_output_view = pn.indicators.Number(
    name="Power Output",
    value=power_output,
    format="{value} MW",
    colors=[
        (power_output, ACCENT),
        (max(POWER_OUTPUTS), "red"),
    ],
)
indicators = pn.FlexBox(wind_speed_view, power_output_view)
indicators
```

We create [`Number`](../../reference/indicators/Number.ipynb) indicators to display the wind speed and power output. The [`FlexBox`](../../reference/layouts/FlexBox.ipynb) layout will arrange the indicators horizontally or vertically depending on the screen size.

::::{tab-set}

:::{tab-item} Script
:sync: script

```python
pn.template.FastListTemplate(
    title="WTG Monitoring Dashboard",
    main=[indicators],
    accent=ACCENT,
    main_layout=None,
    theme="dark",
    theme_toggle=False,
    meta_refresh="2",  # Automatically refresh every 2 seconds
).servable()
```

:::

:::{tab-item} Notebook
:sync: notebook

```python
pn.template.FastListTemplate(
    title="WTG Monitoring Dashboard",
    main=[indicators],
    accent=ACCENT,
    main_layout=None,
    theme="dark",
    theme_toggle=False,
    meta_refresh="2",  # Automatically refresh every 2 seconds
).servable();  # The ; is only needed if used in a notebook
```

:::

::::

Finally, we construct the dashboard using the [`FastListTemplate`](../../reference/templates/FastListTemplate.ipynb). We set the accent color, theme, and enable automatic refreshing every 2 seconds.

:::{note}
In the example, we use a `meta_refresh` rate of 2 for illustration purposes. For real use cases, we recommend `meta_refresh` rates of 15 or above. For lower refresh rates we would be using a [*Periodic Callback*](../../how_to/callbacks/periodic.md) or [*generators*](../../how_to/interactivity/bind_generators.md) in combination with a `meta_refresh` rate of 900 or above.
:::

## Serve the App

Now serve the app with:

::::{tab-set}

:::{tab-item} Script
:sync: script

```bash
panel serve app.py --autoreload
```

:::

:::{tab-item} Notebook
:sync: notebook

```bash
panel serve app.ipynb --autoreload
```

:::

::::

Open [http://localhost:5006/app](http://localhost:5006/app)

It should resemble

![Monitoring Dashboard](https://assets.holoviz.org/panel/tutorials/build-monitoring-dashboard.gif)

## Recap

In this tutorial, we have built a basic monitoring dashboard that *refreshes* the entire page periodically. We have used  `pn.panel`, the [`Number`](../../reference/indicators/Number.ipynb) *indicator* and the [`FastListTemplate`](../../reference/templates/FastListTemplate.ipynb).

We used the `meta_refresh` argument of the [FastListTemplate](../../reference/templates/FastListTemplate.ipynb) to automatically *refresh* the dashboard periodically.
