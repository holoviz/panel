# React to User Input

Welcome to the interactive world of Panel! In this section, you'll learn how to make your Panel applications come alive by reacting to user input. We'll explore how to bind widgets to a function and add side effects using the `watch` parameter in Panel.

## Embrace `pn.bind`

The `pn.bind` method is your gateway to interactive Panel applications. It enables you to connect widgets to functions seamlessly, triggering updates whenever the widget values change. Let's dive into an example:

```{pyodide}
import panel as pn

pn.extension()

def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return (
        f"Wind Speed: {wind_speed} m/s, "
        f"Efficiency: {efficiency}, "
        f"Power Generation: {power_generation:.1f} kW"
    )

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

power = pn.bind(
    calculate_power, wind_speed=wind_speed, efficiency=efficiency
)

pn.Column(wind_speed, power).servable()
```

As you interact with the slider, notice how the displayed power generation dynamically updates, reflecting changes in wind speed.

You can of course bind to multiple widgets. Let's make the `efficiency` a widget:

```{pyodide}
import panel as pn

pn.extension()

def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return (
        f"Wind Speed: {wind_speed} m/s, "
        f"Efficiency: {efficiency}, "
        f"Power Generation: {power_generation:.1f} kW"
    )

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")

power = pn.bind(
    calculate_power, wind_speed=wind_speed, efficiency=efficiency
)

pn.Column(wind_speed, efficiency, power).servable()
```

## Using References

Bound functions can be displayed directly as we have done above or they can be used as references when passed to a Panel component. This approach is usually more efficient since we only have to update the specific parameter:

```{pyodide}
import panel as pn

pn.extension()

def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return (
        f"Wind Speed: {wind_speed} m/s, "
        f"Efficiency: {efficiency}, "
        f"Power Generation: {power_generation:.1f} kW"
    )

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")

power = pn.bind(
    calculate_power, wind_speed=wind_speed, efficiency=efficiency
)

power_md = pn.widgets.Markdown(power)

pn.Column(wind_speed, efficiency, power_md).servable()
```

Note how we pass the bound function as an argument to the `Markdown` pane.

## Crafting Interactive Forms

Forms are powerful tools for collecting user inputs. With Panel, you can easily create forms and process them after they are submitted:

```{pyodide}
import panel as pn

pn.extension()

def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return (
        f"Wind Speed: {wind_speed} m/s, "
        f"Efficiency: {efficiency}, "
        f"Power Generation: {power_generation:.1f} kW"
    )

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")

power = pn.bind(
    calculate_power, wind_speed=wind_speed, efficiency=efficiency
)

submit = pn.widgets.Button(name="Submit", button_type="primary")

def result(clicked):
    if clicked:
        return power()
    return "Click Submit"

result = pn.pane.Markdown(pn.bind(result, submit))

pn.Column(
    wind_speed, efficiency, submit, result
).servable()
```

Notice how the text is updated only when the Submit Button is clicked.

## Harnessing Throttling for Performance

To prevent excessive updates and ensure smoother performance, you can apply throttling by binding the `value_throttled` parameter. This limits the rate at which certain actions or events occur, maintaining a balanced user experience:

```{pyodide}
import panel as pn

from time import sleep

pn.extension()

def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return (
        f"Wind Speed: {wind_speed} m/s, "
        f"Efficiency: {efficiency}, "
        f"Power Generation: {power_generation:.1f} kW"
    )

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_bnd = pn.bind(
    calculate_power, wind_speed=wind_speed.param.value_throttled, efficiency=efficiency
)

power_md = pn.pane.Markdown(power)

pn.Column(wind_speed, power_md).servable()
```

Try dragging the slider. Notice that the `calculate_power` function is only run when you release the mouse.

### Binding to bound functions

You may also `bind` to bound functions. This can help you break down you reactivity into smaller, reusable steps.

```{pyodide}
import panel as pn

pn.extension()

def calculate_power(wind_speed, efficiency):
    return wind_speed * efficiency

def format_power_gen(wind_speed, efficiency, power):
    return (
        f"Wind Speed: {wind_speed} m/s, "
        f"Efficiency: {efficiency}, "
        f"Power Generation: {power:.1f} kW"
    )

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

power = pn.bind(calculate_power, wind_speed, efficiency)

power_text = pn.bind(format_power_gen, wind_speed, efficiency, power)

pn.Column(wind_speed, power, power_text).servable()
```

:::{warning}
Binding to bound functions can help you to quickly explore your data, but its highly inefficient as the results are calculated from scratch for each call.
:::

Try changing the `power_generation` function to:

```python
def power_generation(wind_speed, efficiency):
    print(wind_speed, efficiency)
    return wind_speed * efficiency
```

Try dragging the `wind_speed` slider. Notice that the `power_generation` function is called twice every time you change the `wind_speed` `value`.

To solve this problem you should add *caching* (`pn.cache`) or use *reactive expressions* (`pn.rx`). You will learn about *reactive expressions* in the next section.

## Triggering Side Effects with `watch`

When you need to trigger additional tasks in response to user actions, setting `watch` comes in handy:

```{pyodide}
import panel as pn

pn.extension()

submit = pn.widgets.Button(name="Start the wind turbine")

def start_stop_wind_turbine(clicked):
    if submit.clicks % 2:
        submit.name = "Start the wind turbine"
    else:
        submit.name = "Stop the wind turbine"

pn.bind(start_stop_wind_turbine, submit, watch=True)

pn.Column(submit).servable()
```

```{warning}
In the example provided, our side effect directly modifies the UI by altering the name of the Button. However, this approach indicates poor architectural design.

It's advisable to avoid directly updating the UI through side effects. Instead, focus on updating the application's *state*, allowing the UI to respond automatically to any changes in the state. The concept of state will be explored further in the subsequent section.
```

If your task is long running your might want to disable the `Button` and add a loading indicator while the task is running.

```{pyodide}
from time import sleep

import panel as pn

pn.extension()

submit = pn.widgets.Button(name="Start the wind turbine")

def start_stop_wind_turbine(clicked):
    with submit.param.update(loading=True, disabled=True):
        sleep(2)
        if bool(submit.clicks%2):
            submit.name = "Start the wind turbine"
        else:
            submit.name = "Stop the wind turbine"

pn.bind(start_stop_wind_turbine, submit, watch=True)

pn.Column(submit).servable()
```

### Keep the UI responsive with threads or processes

To keep your UI and server responsive while the long running, blocking task is running you might want to run it asynchronously in a separate thread:

```python
from time import sleep

import asyncio

import panel as pn

pn.extension()

submit = pn.widgets.Button(name="Start the wind turbine")

async def start_stop_wind_turbine(clicked):
    with submit.param.update(loading=True, disabled=True):
        result = await asyncio.to_thread(sleep, 5)

        if submit.clicks % 2:
            submit.name = "Start the wind turbine"
        else:
            submit.name = "Stop the wind turbine"

pn.bind(start_stop_wind_turbine, submit, watch=True)

pn.Column(submit).servable()
```

:::{note}
In the example we use a `asyncio.to_thread` this should work great if your blocking task releases the GIL while running. Tasks that request data from the web or read data from files typically do this. Some computational methods from Numpy, Pandas etc. also release the GIL. If your long running task does not release the GIL you may have to use a `ProcessPoolExecutor` instead. This introduces some overhead though.
:::

## Recap

You've now unlocked the power of interactivity in your Panel applications:

- `pn.bind(some_function, widget_1, widget_2)`: for seamless updates based on widget values.
- `pn.bind(some_task, some_widget, watch=True)`: for triggering tasks in response to user actions.
- Throttling ensures smoother performance by limiting update frequency.
- Utilizing async and threading keeps your UI responsive during long-running tasks.

Now, let your imagination run wild and craft dynamic, engaging Panel applications!

## Resources

### How-to

- [Add interactivity to a function](../../how_to/interactivity/bind_function.md)
- [Add Interactivity with `pn.bind` | Migrate from Streamlit](../../how_to/streamlit_migration/interactivity.md)
- [Enable Throttling](../../how_to/performance/throttling.md)
- [Run synchronous functions asynchronously](../../how_to/concurrency/sync_to_async.md)
- [Setup Manual Threading](../../how_to/concurrency/manual_threading.md)
- [Use Asynchronous Callbacks](../../how_to/callbacks/async.md)

### Explanation

- [Reactivity in Panel](../../explanation/api/reactivity.md)

### External

- [Param: Parameters and `param.bind`](https://param.holoviz.org/user_guide/Reactive_Expressions.html#parameters-and-param-bind)
