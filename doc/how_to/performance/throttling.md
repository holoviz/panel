# Enable Throttling

One of the simplest ways to avoid slowing down your application is simply to control how often events from the frontend trigger code execution in Python. Particularly when using sliders this can be a problem. To solve this issue sliders offer `value_throttled` parameters which are updated only when the user releases the slider unlike the `value` parameter which is updated continuously as the slider is dragged. If you are building apps using the reactive `pn.bind` function you can depend on the `value_throttled` parameter directly:

```{pyodide}
import panel as pn
pn.extension()

def output(value):
    return value

slider = pn.widgets.IntSlider(end=10)
bound_output = pn.bind(output, slider.param.value_throttled)
pn.Row(slider, bound_output)
```

Alternatively, you can also ensure that all sliders only update on mouse release if you set `pn.config.throttled = True`.
