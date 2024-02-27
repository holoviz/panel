# Build Streaming Dashboard

In this tutorial, we come together to create a simple streaming dashboard to monitor the wind speed and power output of one of our wind turbines:

- We will use `pn.state.add_periodic_callback` to trigger a task to run on a schedule.

:::{note}
When we ask to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook, or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Install the Dependencies

Please ensure that [SciPy](https://scipy.org/) is installed.

::::{tab-set}

:::{tab-item} conda
:sync: conda

``` bash
conda install -y -c conda-forge panel scipy
```

:::

:::{tab-item} pip
:sync: pip

``` bash
pip install panel scipy
```

:::

::::

## Build the App

Run the code below:

```{pyodide}
import numpy as np
import panel as pn
from scipy.interpolate import interp1d

pn.extension()

WIND_SPEEDS = np.array([0, 3, 6, 9, 12, 15, 18, 21])  # Wind speed (m/s)
WIND_SPEED_MEAN = 8
WIND_SPEED_STD_DEV = 0.5
POWER_OUTPUTS = np.array([0, 0.03, 0.20, 0.6, 1.0, 1.0, 0, 0])  # Power output (MW)

# Define State

wind_speed = pn.rx(8.0)

## Extract Data

def get_wind_speed():
    # Replace with your own wind speed source
    return round(
        np.random.normal(WIND_SPEED_MEAN, WIND_SPEED_STD_DEV), 1
    )

## Transform Data

power_interpolation = interp1d(
    WIND_SPEEDS, POWER_OUTPUTS, kind="linear", fill_value="extrapolate"
)

def get_power_output(wind_speed):
    return np.round(power_interpolation(wind_speed), 2)

## View Data

wind_speed_view = pn.indicators.Number(
    name="Wind Speed",
    value=wind_speed,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
)
power_output_view = pn.indicators.Number(
    name="Power Output",
    value=wind_speed.rx.pipe(get_power_output),
    format="{value} MW",
    colors=[(10, "green"), (100, "red")],
)

# Update data periodically

def update_wind_speed():
    wind_speed.rx.value = get_wind_speed()

pn.state.add_periodic_callback(update_wind_speed, period=1000)

# Layout the app

pn.Column(
    "# WTG Monitoring Dashboard",
    pn.FlexBox(wind_speed_view, power_output_view),
).servable()
```

Try changing the `period` from `1000` to `100`.

:::{note}
The code refers to

- `wind_speed = pn.rx(8.0)`: This is a *reactive expression* with an initial value of 8.0. The UI updates whenever the value `wind_speed.rx.value` is changed.
- `pn.state.add_periodic_callback(update_wind_speed, period=1000)`: This updates the `wind_speed_rx.value` every 1000 milliseconds.
:::

## Resources

### How-to

- [Periodically Run Callbacks](../../how_to/callbacks/periodic.md)

### App Gallery

- [Streaming VideoStream](../../gallery/index.md)
