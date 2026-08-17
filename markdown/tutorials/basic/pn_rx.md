# Reactive Expressions

In this section you will learn about `pn.rx`. `pn.rx` extends the concepts from `pn.bind` that your learned in the previous section.

## Embrace `pn.rx`

`pn.rx` allows you to treat any object as a reactive expression. This means we can do things like multiplying a widget (representing the wind speed) with a float value (representing the efficiency) and then format the result all without writing callbacks:

```python
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, label="Wind Speed (m/s)"
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

```python
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, label="Wind Speed (m/s)"
)

efficiency = 0.3

power = wind_speed.rx() * efficiency

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(wind_speed=wind_speed, efficiency=efficiency, power=power)

power_md = pn.pane.Markdown(power_text)

pn.Column(wind_speed, power_md).servable()
```

You can of course write expressions with multiple widgets. Lets make the `efficiency` a widget:

```python
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, label="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(value=0.3, start=0.0, end=1.0, label="Efficiency (kW/(m/s))")

power = wind_speed.rx() * efficiency.rx()

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(wind_speed=wind_speed, efficiency=efficiency, power=power)

power_md = pn.pane.Markdown(power_text)

pn.Column(wind_speed, efficiency, power_md).servable()
```

## Crafting Interactive Forms

Forms are powerful tools for collecting user inputs. With `.rx.when` you can easily defer some calculation (i.e. the form submission) until some event (such as a button click) is triggered:

```python
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, label="Wind Speed (m/s)"
)
efficiency = pn.widgets.FloatInput(
    value=0.3, start=0.0, end=1.0, label="Efficiency (kW/(m/s))"
)
submit = pn.widgets.Button(label="Submit", color="primary")

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

To prevent excessive updates and ensure smoother performance, you can apply throttling (`.value_throttled`). This limits the rate at which certain actions or events occur, maintaining a balanced user experience:

```python
import panel as pn

pn.extension()

wind_speed = pn.widgets.FloatSlider(
    value=5, start=0, end=20, step=1, label="Wind Speed (m/s)"
)
efficiency = 0.3

power = wind_speed.param.value_throttled.rx() * efficiency

power_text = pn.rx(
    "Wind Speed: {wind_speed} m/s, "
    "Efficiency: {efficiency}, "
    "Power Generation: {power:.1f} kW"
).format(
    wind_speed=wind_speed.param.value_throttled,
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

```python
import panel as pn

pn.extension()

# Declare state of application
is_stopped = pn.rx(True)

rx_name = is_stopped.rx.where("Start the wind turbine", "Stop the wind turbine")

submit = pn.widgets.Button(label=rx_name)

def toggle_wind_turbine(clicked):
    is_stopped.rx.value = not is_stopped.rx.value

submit.rx.watch(toggle_wind_turbine)

pn.Column(submit).servable()
```

Here we store the state of the windturbine in a separate `rx` variable, whenever the submit button is clicked we toggle the state.

### Keep the UI responsive with threads or processes

To keep your UI and server responsive while the long running, blocking task is running you might want to run it asyncrounously in a separate thread:

```python
import asyncio
import time

import panel as pn

pn.extension()

is_stopped = pn.rx(True)

submit = pn.widgets.Button(
    label=is_stopped.rx.where("Start the wind turbine", "Stop the wind turbine"),
)

async def start_stop_wind_turbine(clicked):
    with submit.param.update(loading=True, disabled=True):
        await asyncio.to_thread(time.sleep, 1)
        is_stopped.rx.value = not is_stopped.rx.value

submit.rx.watch(start_stop_wind_turbine)

pn.Column(submit).servable()
```

## Recommended Reading

We do recommend you study the explanation document about [reactivity in Panel](../../explanation/api/reactivity.md) and the [`ReactiveExpr` reference guide](../../reference/panes/ReactiveExpr.md) to learn more about displaying reactive expressions in Panel.

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

[`ReactiveExpr` reference guide](../../reference/panes/ReactiveExpr.md)

### How-to

- [Add interactivity to a function](../../how_to/interactivity/bind_function.md)
- [Add Interactivity with `pn.bind` | Migrate from Streamlit](../../how_to/streamlit_migration/interactivity.md)
- [Enable Throttling](../../how_to/performance/throttling.md)
- [Run synchronous functions asynchronously](../../how_to/concurrency/sync_to_async.md)
- [Setup Manual Threading](../../how_to/concurrency/manual_threading.md)
- [Use Asynchronous Callbacks](../../how_to/callbacks/async.md)

### Explanation

- [Reactivity](../../explanation/api/reactivity.md)

### External

- [Param: References](https://param.holoviz.org/user_guide/References.html)
- [Param: Reactive Functions and Expressions](https://param.holoviz.org/user_guide/Reactive_Expressions.html)
