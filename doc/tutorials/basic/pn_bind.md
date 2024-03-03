# React to User Input

In this section, you will learn how to make your Panel applications interactive by reacting to user input. We'll focus on two key aspects: binding functions to widgets and adding side effects using the `watch=True` parameter in Panel.

## `pn.bind`

`pn.bind` allows a developer to indicate that a certain widget should be used as the argument to a function that returns something displayable. Panel will automatically invoke that function when the corresponding widget `value` changes

Run the code below:

```{pyodide}
import panel as pn

pn.extension()


def calculate_power_generation(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_fn = pn.bind(
    calculate_power_generation, wind_speed=wind_speed, efficiency=efficiency
)

print(calculate_power_fn())

wind_speed.value = 10
print(calculate_power_fn())
```

You will notice how the `calculate_power_fn` now uses the `wind_speed.value` and the `efficiency` as its arguments.

Lets now see how Panel automatically invokes the bound function `calculate_power_fn`:

```{pyodide}
import panel as pn

pn.extension()


def calculate_power_generation(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_fn = pn.bind(
    calculate_power_generation, wind_speed=wind_speed, efficiency=efficiency
)

pn.Column(
    wind_speed, calculate_power_fn
).servable()
```

Try dragging the slider.

You can of course bind to multiple widgets Lets make the `efficiency` a widget:

```{pyodide}
import panel as pn

pn.extension()


def calculate_power_generation(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")

calculate_power_fn = pn.bind(
    calculate_power_generation, wind_speed=wind_speed, efficiency=efficiency
)

pn.Column(
    wind_speed, efficiency, calculate_power_fn
).servable()
```

### Display with References

You might want to display the output of a bound function more specifically and efficiently. You can do that by providing the bound function as a *reference* to a Pane.

Lets display using a `Str` pane.

```python
import panel as pn

pn.extension()


def calculate_power_generation(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_fn = pn.bind(
    calculate_power_generation, wind_speed=wind_speed, efficiency=efficiency
)

pn.Column(
    wind_speed, calculate_power_fn, pn.pane.Str(calculate_power_fn)
).servable()
```

### Create Forms

```{info}
An *HTML form* is like a digital questionnaire where users input information. It consists of fields like text boxes, checkboxes, and buttons. When the form is *submitted*, the data is processed.
```

Sometimes you want the user to input information via multiple widgets before you process the input. You can do this by adding a Button and update when the user clicks the Button.

```{pyodide}
import panel as pn

pn.extension()


def calculate_power_generation(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")

calculate_power_fn = pn.bind(
    calculate_power_generation, wind_speed=wind_speed, efficiency=efficiency
)

submit = pn.widgets.Button(name="Submit")

def result(clicked):
    if clicked:
        return calculate_power_fn()
    return "Click Submit"

result_fn = pn.bind(result, submit)

pn.Column(
    wind_speed, efficiency, submit, result_fn
).servable()
```

### Apply Throttling

```{info}
*Throttling* refers to controlling the rate at which certain actions or events can occur. It limits the frequency of updates or interactions, preventing overwhelming system resources or excessive data processing. Throttling ensures smoother performance and avoids overloading the application, maintaining a balanced user experience.
```

Lets assume calculating the `power_generation` is slow

```{pyodide}
import panel as pn
from time import sleep

pn.extension()


def calculate_power_generation(wind_speed, efficiency):
    print("calculate", wind_speed)
    sleep(1)
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_fn = pn.bind(
    calculate_power_generation, wind_speed=wind_speed, efficiency=efficiency
)

pn.Column(
    wind_speed, calculate_power_fn
).servable()
```

Try dragging the slider. You will notice from the output in the terminal that the `calculate_power_generation` function is run multiple times when you drag the slider.

To only update when you stop dragging and release the mouse you can use *throttling*.

```{pyodide}
import panel as pn
from time import sleep

pn.extension()


def calculate_power_generation(wind_speed, efficiency):
    print("calculate", wind_speed)
    sleep(1)
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_fn = pn.bind(
    calculate_power_generation, wind_speed=wind_speed.param.value_throttled, efficiency=efficiency
)

pn.Column(
    wind_speed, calculate_power_fn
).servable()
```

Try dragging the slider. You will notice how the `calculate_power_generation` function is only run when the mouse is released.

```{tip}
You can change the global configuration of Panel to use *throttling* via `pn.config.throttled=True` or `pn.extension(throttled=True)`.
```

### Binding to bound functions

You may also `bind` to bound functions. This can help you break down you reactivity into smaller, reusable steps.

```{pyodide}
import panel as pn

pn.extension()

def power_generation(wind_speed, efficiency):
    print(wind_speed, efficiency)
    return wind_speed * efficiency

def power_generation_text(wind_speed, efficiency, power):
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power:.1f} kW"

def to_html(text):
    return f"<strong>{text}<strong>"

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

b_power_generation = pn.bind(power_generation, wind_speed=wind_speed, efficiency=efficiency)

b_power_generation_text = pn.bind(power_generation_text, wind_speed, efficiency, b_power_generation)

pn.Column(
    wind_speed, b_power_generation, b_power_generation_text
).servable()
```

```{warning}
Binding to bound functions can help you to quickly explore your data but its highly inefficient as the results are calculated from scratch for each call.
```

Try changing the `power_generation` function to:

```python
def power_generation(wind_speed, efficiency):
    print(wind_speed, efficiency)
    return wind_speed * efficiency
```

Try dragging the `wind_speed` slider. Notice that the `power_generation` function is called twice every time you change the `wind_speed` `value`.

To solve this problem you should be using *reactive expressions* (`pn.rx`) instead. You will learn about *reactive expressions* in the next section.

### Running side effects with `watch=True`

Sometimes you might want to trigger a *side effect*, i.e. run a separate task. You can trigger a side effects by setting `watch=True`:

```{pyodide}
import panel as pn

pn.extension()

submit = pn.widgets.Button(name="Start the wind turbine")

def start_stop_wind_turbine(clicked):
    if bool(submit.clicks%2):
        submit.name="Start the wind turbine"
    else:
        submit.name="Stop the wind turbine"

b_stop_wind_turbine = pn.bind(start_stop_wind_turbine, submit, watch=True)


pn.Column(submit).servable()
```

```{warning}
In the example above our sideeffect updated the UI directly by changing the name of the Button. This is a sign of bad architecture.

We recommend sideeffects not to update the UI directly. Instead you should be updating the *state* and the UI should be updating automatically in response to the state change. You will learn more about state in the next section.
```

If your task is long running your might want to disable the Button while the task is running.

```{pyodide}
import panel as pn
from time import sleep

pn.extension()

submit = pn.widgets.Button(name="Start the wind turbine")

def start_stop_wind_turbine(clicked):
    with submit.param.update(loading=True, disabled=True):
        sleep(2)
        if bool(submit.clicks%2):
            submit.name="Start the wind turbine"
        else:
            submit.name="Stop the wind turbine"

b_stop_wind_turbine = pn.bind(start_stop_wind_turbine, submit, watch=True)


pn.Column(submit).servable()
```

To keep your UI and server responsive while the long running, blocking task is running you might want to run it asyncrounously in a separate thread:

```python
import asyncio
import concurrent.futures
from time import sleep

import panel as pn

pn.extension()

submit = pn.widgets.Button(name="Start the wind turbine")


async def start_stop_wind_turbine(clicked):
    with submit.param.update(loading=True, disabled=True):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(sleep, 5)
            result = await asyncio.wrap_future(future)

        if bool(submit.clicks % 2):
            submit.name = "Start the wind turbine"
        else:
            submit.name = "Stop the wind turbine"


b_stop_wind_turbine = pn.bind(start_stop_wind_turbine, submit, watch=True)


pn.Column(submit).servable()
```

:::{note}
In the example we use a `ThreadPoolExecutor` this should work great if your blocking task releases the GIL while running. Tasks that request data from the web or read data from files typically do this. Some computational methods from Numpy, Pandas etc. also release the GIL. If your long running task does not release the GIL you might want to replace the `ThreadPoolExecutor` with a `ProcessPoolExecutor`. This introduces some overhead though.
:::

## Resources

### How-to

- [Add interactivity to a function](../../how_to/interactivity/bind_function.md)
- [Enable Throttling](../../how_to/performance/throttling.md)
- [Run synchronous functions asynchronously](../../how_to/concurrency/sync_to_async.md)
- [Setup Manual Threading](../../how_to/concurrency/manual_threading.md)
- [Use Asynchronous Callbacks](../../how_to/callbacks/async.md)

### Explanation

- [Reactive API](../../explanation/api/reactive.md)
