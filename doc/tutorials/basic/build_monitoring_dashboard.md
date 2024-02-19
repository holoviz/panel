# Build a Monitoring Dashboard

In this tutorial, we will build a *display only* dashboard that *refreshes* the entire page periodically.

These kinds of dashboards can be displayed on a big screen running 24/7 in for example a call center, control room or trading area.

## Install the Dependencies

Please make sure [SciPy](https://scipy.org/) is installed.

::::{tab-set}

:::{tab-item} conda
:sync: conda

``` bash
conda install -y -c conda-forge scipy
```

:::

:::{tab-item} pip
:sync: pip

``` bash
pip install scipy
```

:::

::::

## Build the App

Copy the code below to a file named `app.py`:

```python
import numpy as np
import panel as pn
from scipy.interpolate import interp1d

ACCENT="teal"

WIND_SPEED_STD_DEV = 2.0
WIND_SPEED_MEAN = 8.0

WIND_SPEEDS = np.array([0, 3, 6, 9, 12, 15, 18, 21])  # Wind speed (m/s)
POWER_OUTPUTS = np.array([0,39,260,780, 1300, 1300, 0, 0])  # Power output (MW)

# Extract Data

def get_wind_speed():
    # Replace with your own wind speed source
    return round(np.random.normal(WIND_SPEED_MEAN, WIND_SPEED_STD_DEV), 1)

wind_speed = get_wind_speed()

# Transform Data

def get_power_output(wind_speed):
    # Replace with your own power output calculation
    power_interpolation = interp1d(
        WIND_SPEEDS, POWER_OUTPUTS, kind="linear", fill_value="extrapolate"
    )
    return np.round(power_interpolation(wind_speed), 1)

power_output = get_power_output(wind_speed)

## View Data

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

## Layout and style with a template

pn.template.FastListTemplate(
    title="WTG Monitoring Dashboard",
    main=[
        pn.FlexBox(wind_speed_view, power_output_view),
    ],
    accent=ACCENT,
    main_layout=None,
    theme="dark",
    theme_toggle=False,
    meta_refresh="10", # Automatically refresh every 10 seconds
).servable(); # The ; is only needed if used in a notebook
```

Serve the `app.py` file with

```bash
panel serve app.py --autoreload
```

Open [http://localhost:5006/app](http://localhost:5006/app)

It should look like

![WTG Monitoring Dashboard](../../_static/images/monitoring_dashboard.png)

You will notice it automatically refreshes every 10 seconds.

Try changing `meta_refresh="10"` to `meta_refresh="5"`. What happens?

## Break it down

We display the *wind speed* with a [`Number`](../../reference/indicators/Number.ipynb) *indicator*

```python
wind_speed_view = pn.indicators.Number(
    name="Wind Speed",
    value=wind_speed,
    format="{value} m/s",
    colors=[(10, ACCENT), (100, "red")],
)
```

We use the [`FastListTemplate`](../../reference/templates/FastListTemplate.ipynb) to easily layout and style the dashboard.

Here we use the `meta_refresh` argument to instruct the browser to automatically refresh the page every 10 seconds.

```python
    meta_refresh="10",
```

:::{tip}
Using the `meta_refresh` argument can be a really *simple* and *robust* way to build a *display-only* dashboard for a call center, control room or trading area.
:::

## Recap

In this tutorial, we have built a basic monitoring dashboard that *refreshes* the entire page periodically. We have used  `pn.panel`, the [`Number`](../../reference/indicators/Number.ipynb) *indicator* and the [`FastListTemplate`](../../reference/templates/FastListTemplate.ipynb).

We used the `meta_refresh` argument of the [FastListTemplate](../../reference/templates/FastListTemplate.ipynb) to automatically *refresh* the dashboard periodically.

## Resources

- [FastListTemplate](../../reference/templates/FastListTemplate.ipynb)
