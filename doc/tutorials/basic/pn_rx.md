# Reactive Expressions

In this section you will learn about `pn.rx`. `pn.rx` extends the concepts from `pn.bind` that your learned in the previous section.

:::{note}
You might feel some repetition from the previous section on `pn.bind`. We do this on purpose to enable you to compare and contrast. `pn.rx` is the new, and much more flexibly big brother of `pn.bind`. But `pn.bind` has been the core API in Panel for a long time, so you will meet it across our documentation and community sites, and thus its very important to learn.

`pn.rx` will enable you to build more complicated applications using a more flexible and maintainable architecture.
:::

## Embrace `pn.rx`

`pn.rx` allows you to treat any object as a reactive expression. This means we can do things like multiplying a widget (representing the wind speed) with a float value (representing the efficiency) and then format the result all without writing callbacks:

```{pyodide}
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

power = wind_speed.rx() * efficiency

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(wind_speed=wind_speed, efficiency=efficiency, power=power)

pn.Column(power_text).servable()
```

You will notice how adding `power_text` to the `Column` displays both the widget and the bound function.

To separate the widget and bound function we can use the `power_text` as a reference when we construct a `Markdown` pane:

```{pyodide}
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)

efficiency = 0.3

power = wind_speed.rx() * efficiency

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(wind_speed=wind_speed, efficiency=efficiency, power=power)

power_md = pn.pane.Markdown(calculate_power_rx)

pn.Column(wind_speed, power_md).servable()
```

You can of course write expressions with multiple widgets. Lets make the `efficiency` a widget:

```{pyodide}
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))")

power = wind_speed.rx() * efficiency.rx()

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(wind_speed=wind_speed, efficiency=efficiency, power=power)

power_md = pn.pane.Markdown(calculate_power_rx)

pn.Column(wind_speed, efficiency, power_md).servable()
```

## Crafting Interactive Forms

Forms are powerful tools for collecting user inputs. With `.rx.when` you can easily defer some calculation (i.e. the form submission) until some event (such as a button click) is triggered:

```{pyodide}
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(
    value=0.3, start=0.0, end=1.0, name="Efficiency (kW/(m/s))"
)
submit = pn.widgets.Button(name="Submit")

power = wind_speed.rx() * efficiency.rx()

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(
    wind_speed=wind_speed,
    efficiency=efficiency,
    power=power
).rx.when(submit)

pn.Column(
    wind_speed, efficiency, submit, pn.pane.Markdown(power_text)
).servable()
```

Try changing some of the inputs and clicking the submit Button. Try again. Notice how the text is only updated when we click the submit Button - we used `.rx.when` to achieve this effect.

## Harnessing Throttling for Performance

To prevent excessive updates and ensure smoother performance, you can apply throttling. This limits the rate at which certain actions or events occur, maintaining a balanced user experience:

```{pyodide}
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, name="Wind Speed (m/s)"
)
efficiency = 0.3

power = wind_speed.rx() * efficiency

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(
    wind_speed=wind_speed.param.value,
    efficiency=0.3,
    power=power
)

pn.Column(
    wind_speed, pn.pane.Markdown(power_text)
).servable()
```

Try dragging the slider. Notice that the text is only updated when you release the mouse.

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
from time import sleep

import panel as pn

pn.extension()

is_stopped = pn.rx(True)

submit = pn.widgets.Button(
    name=is_stopped.rx.where("Start the wind turbine", "Stop the wind turbine"),
)

async def start_stop_wind_turbine(clicked):
    with submit.param.update(loading=True, disabled=True):
        await asyncio.to_thread(sleep, 1)
        is_stopped.rx.value = not is_stopped.rx.value

submit.rx.watch(start_stop_wind_turbine)

pn.Column(submit).servable()
```

:::{note}
In the example we use a `asyncio.to_thread` this should work great if your blocking task releases the GIL while running. Tasks that request data from the web or read data from files typically do this. Some computational methods from Numpy, Pandas etc. also release the GIL. If your long running task does not release the GIL you may have to use a `ProcessPoolExecutor` instead. This introduces some overhead though.
:::

## Recommended Reading

We do recommend you study the [`ReactiveExpr` reference guide](../../reference/panes/ReactiveExpr.ipynb) to learn more about displaying reactive expressions in Panel.

## Recap

You've now unlocked the power of interactivity in your Panel applications:

- `some_widget.rx()`: for seamless updates based on widget values.
- `pn.rx(some_function)(widget_1, widget_2)`: for seamless updates based on widget values.
- `pn.rx(some_task, some_widget).rx.watch()`: for triggering tasks in response to user actions.
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
