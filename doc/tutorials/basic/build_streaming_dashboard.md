# Build Streaming Dashboard

In this tutorial we build a simple streaming dashboard to monitor the wind speed and power output of one of your wind turbines.

:::{note}
When I ask you to *run the code* in the sections below, you may either execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Build the App

```
import numpy as np
import panel as pn
from scipy.interpolate import interp1d

pn.extension()

WIND_SPEEDS = np.array([0, 3, 6, 9, 12, 15, 18, 21])  # Wind speed (m/s)
WIND_SPEED_STD_DEV = 0.5
POWER_OUTPUTS = np.array([0, 0.03, 0.20, 0.6, 1.0, 1.0, 0, 0])  # Power output (MW)

wind_speed = pn.rx(8.0)

def update_wind_speed():
    # Replace with your own wind speed source
    wind_speed.rx.value = round(
        np.random.normal(wind_speed.rx.value, WIND_SPEED_STD_DEV), 1
    )
pn.state.add_periodic_callback(update_wind_speed, period=1000)

## Transformations

power_interpolation = interp1d(
    WIND_SPEEDS, POWER_OUTPUTS, kind="linear", fill_value="extrapolate"
)

def get_power_output(wind_speed):
    return np.round(power_interpolation(wind_speed), 2)

## Views

wind_speed_view = pn.indicators.Number(
    name="Wind Speed",
    value=wind_speed,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
)
power_output_view = pn.indicators.Number(
    name="Power Output",
    value=pn.bind(get_power_output, wind_speed),
    format="{value} MW",
    colors=[(10, "green"), (100, "red")],
)


pn.Column(
    "# WTG Monitoring Dashboard",
    pn.FlexBox(wind_speed_view, power_output_view),
).servable()
```

TODO

Figure out if its possible to create a very simple version where the focus is on the display. Too many things used that the user has not learned yet. Also figure out how to best make this scale. The periodic callback should really run once for all users. How to do that in a single file?
