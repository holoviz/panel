# Enable Throttling

One of the simplest ways to avoid slowing down your application is simply to control how often events from the frontend trigger code execution in Python. Particularly when using sliders this can be a problem. To solve this issue sliders offer `value_throttled` parameters which are updated only when the user releases the slider unlike the `value` parameter which is updated continuously as the slider is dragged. If you are building apps using the reactive `pn.bind` or `pn.depends` functions you can depend on the `value_throttled` parameter directly:

```python
slider = pn.widgets.IntSlider()

def output(value):
    return ...

pn.bind(output, slider.param.value_throttled)
```

Alternatively you can also ensure that all sliders only update on mouse release if you set `pn.config.throttled = True`.
