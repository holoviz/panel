# Reactive Expressions

In this section you will learn about `pn.rx`. `pn.rx` extends the concepts from `pn.bind` that your learned in the previous section.

:::{note}
You might feel some repetition from the previous section on `pn.bind`. We do this on purpose to enable you to compare and contrast. `pn.rx` is the new, and much more flexibly big brother of `pn.bind`. But `pn.bind` has been the core api in Panel for a long time, so you will meet it across our documentation and community sites, and thus its very important to learn.

`pn.rx` will enable you to build more complicated applications using a more flexible and maintainable architecture.
:::

## Embrace `pn.rx`

```{pyodide}
import panel as pn

pn.extension()

def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_rx = pn.rx(calculate_power)(wind_speed=wind_speed, efficiency=efficiency)

pn.Column(
    calculate_power_rx
).servable()
```

You will notice how adding `calculate_power_rx` to the `Column` displays both the widget and the bound function.

To separate the widget and bound function we use the `calculate_power_rx` as a reference to a Pane:

```{pyodide}
import panel as pn

pn.extension()

def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_rx = pn.rx(calculate_power)(wind_speed=wind_speed, efficiency=efficiency)

pn.Column(
    wind_speed, pn.pane.Markdown(calculate_power_rx)
).servable()
```

:::{note}
If you want all your reactive expressions displayed without widgets you can disable the widgets by setting

```python
pn.ReactiveExpr.show_widgets=False
```

:::

You can of course bind to multiple widgets Lets make the `efficiency` a widget:

```{pyodide}
import panel as pn

pn.extension()


def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")

calculate_power_rx = pn.rx(calculate_power)(wind_speed=wind_speed, efficiency=efficiency)

pn.Column(
    wind_speed, efficiency, pn.pane.Markdown(calculate_power_rx)
).servable()
```

## Crafting Interactive Forms

Forms are powerful tools for collecting user inputs. With Panel, you can easily create forms and process their submissions:

```{pyodide}
import panel as pn

pn.extension()


def calculate_power(wind_speed, efficiency):
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")
submit = pn.widgets.Button(name="Submit")

calculate_power_rx = pn.rx(calculate_power)(wind_speed=wind_speed, efficiency=efficiency)


result_fn = calculate_power_rx.rx.when(submit)

pn.Column(
    wind_speed, efficiency, submit, pn.pane.Markdown(result_fn)
).servable()
```

Try changing some of the inputs and clicking the submit Button. Try again. Notice how the `calculate_power_rx` is only run when we click the submit Button - we used `.when` to achieve this effect.

## Harnessing Throttling for Performance

To prevent excessive updates and ensure smoother performance, you can apply throttling. This limits the rate at which certain actions or events occur, maintaining a balanced user experience:

```{pyodide}
import panel as pn
from time import sleep

pn.extension()


def calculate_power(wind_speed, efficiency):
    print("calculate", wind_speed)
    sleep(1)
    power_generation = wind_speed * efficiency
    return f"Wind Speed: {wind_speed} m/s, Efficiency: {efficiency}, Power Generation: {power_generation:.1f} kW"


wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

calculate_power_rx = pn.rx(calculate_power)(wind_speed=wind_speed.param.value_throttled, efficiency=efficiency)

pn.Column(
    wind_speed, pn.pane.Markdown(calculate_power_rx)
).servable()
```

Try dragging the slider. Notice that the `calculate_power` function is only run when you release the mouse.

### Binding to reactive expressions

You might want to break down your reactive expressions into smaller sub reactive expressions for better reusability and maintainability.

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

power_generation_rx = pn.rx(power_generation)(wind_speed=wind_speed, efficiency=efficiency)

power_generation_text_rx = pn.rx(power_generation_text)(wind_speed, efficiency, power_generation_rx)

pn.Column(
    wind_speed, pn.pane.Str(power_generation_rx), pn.pane.Markdown(power_generation_text_rx)
).servable()
```

If you look in the terminal you will see that `pn.rx` only reruns your functions once every time you change an input widget. This is a big contrast to `pn.bind` which might rerun the functions multiple times.

## Triggering Side Effects with `.watch`

When you need to trigger additional tasks in response to user actions, using `.watch` comes in handy:

```{pyodide}
import panel as pn

pn.extension()

# Declare state of application
is_stopped=pn.rx(True)

def name(stopped):
    if stopped:
        return "Start the wind turbine"
    else:
        return "Stop the wind turbine"

rx_name = pn.rx(name)(is_stopped)

submit = pn.widgets.Button(name=rx_name)

def start_stop_wind_turbine(clicked):
    print("running action")
    is_stopped.rx.value = not is_stopped.rx.value

submit.rx.watch(start_stop_wind_turbine)

pn.Column(submit).servable()
```

:::{tip}
We recommend using this recommended approach when developing more dynamic applications. Applications are easier to reason about when the application displays according to the state instead of being changed directly.
:::

### Keep the UI responsive with threads or processes

To keep your UI and server responsive while the long running, blocking task is running you might want to run it asyncrounously in a separate thread:

```python
import asyncio
import concurrent.futures
from time import sleep

import panel as pn

pn.extension()

is_stopped = pn.rx(True)
is_active = pn.rx(False)


def name(stopped):
    if stopped:
        return "Start the wind turbine"
    else:
        return "Stop the wind turbine"


rx_name = pn.rx(name)(is_stopped)

submit = pn.widgets.Button(name=rx_name, disabled=is_active, loading=is_active)


async def start_stop_wind_turbine(clicked):
    if not clicked:
        return
    is_active.rx.value = True
    with submit.param.update(loading=True, disabled=True):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(sleep, 1)
            result = await asyncio.wrap_future(future)

        is_stopped.rx.value = not is_stopped.rx.value
    is_active.rx.value = False
    print("done")


# Todo: Fix https://github.com/holoviz/param/issues/913
submit.rx.watch(start_stop_wind_turbine)

pn.Column(submit).servable()
```

:::{note}
In the example we use a `ThreadPoolExecutor` this should work great if your blocking task releases the GIL while running. Tasks that request data from the web or read data from files typically do this. Some computational methods from Numpy, Pandas etc. also release the GIL. If your long running task does not release the GIL you might want to replace the `ThreadPoolExecutor` with a `ProcessPoolExecutor`. This introduces some performance overhead though.
:::

## Recommended Reading

We do recommend you study the [`ReactiveExpr` reference guide](../../reference/panes/ReactiveExpr.ipynb) to learn more about displaying reactive expressions in Panel.

## Recap

You've now unlocked the power of interactivity in your Panel applications:

**Todo: Finalize when reactive api has been fixed**

- `pn.rx(some_function)(widget_1, widget_2)`: for seamless updates based on widget values.
- `pn.rx(some_task, some_widget, watch=True)`: for triggering tasks in response to user actions.
- Throttling ensures smoother performance by limiting update frequency.
- Utilizing async and threading keeps your UI responsive during long-running tasks.

Now, let your imagination run wild and craft dynamic, engaging Panel applications!

## Resources

### Reference Guides

[`ReactiveExpr` reference guide](../../reference/panes/ReactiveExpr.ipynb)

### How-to

- [Add interactivity to a function](../../how_to/interactivity/bind_function.md)
- [Add Interactivity with `pn.bind` | Migrate from Streamlit](../../how_to/streamlit_migration/interactivity.md)
- [Enable Throttling](../../how_to/performance/throttling.md)
- [Run synchronous functions asynchronously](../../how_to/concurrency/sync_to_async.md)
- [Setup Manual Threading](../../how_to/concurrency/manual_threading.md)
- [Use Asynchronous Callbacks](../../how_to/callbacks/async.md)

### Explanation

- [Reactive API](../../explanation/api/reactive.md)

### External

- [Param: Reactive Functions and Expressions](https://param.holoviz.org/user_guide/Reactive_Expressions.html)
