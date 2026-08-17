# Progress
---
```python
import panel as pn
pn.extension()
```

The ``Progress`` widget displays the progress towards some target based on the current `value` and the `max` value. If no `value` is set or a `value` of -1 is set the ``Progress`` widget is in indeterminate mode and will animate if `active` is set to True.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``active``** (boolean): Whether to animate the bar when in indeterminate mode
* **``bar_color``** (str): The color of the bar, one of 'primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark'
* **``max``** (int): The maximum progress value
* **``style``** (dict): A dictionary of CSS to apply to the progress bar
* **``value``** (int): The current value towards the progress, set to -1 for an indeterminate state

___

The `Progress` widget can be instantiated with and without a value. If given a `value` the progress bar will fill according to the progress to the `max` value which is 100 by default:

```python
progress = pn.indicators.Progress(label='Progress', value=20, width=200)
progress
```

The progress `value` can be updated from Python:

```python
progress.value = 80
```

The `Progress` can also be instantiated without a `value`:

```python
indeterminate = pn.indicators.Progress(label='Indeterminate Progress', active=True, width=200)
indeterminate
```

The `Progress` widget also supports a range of bar colors:

```python
running = pn.Column(*[
    pn.Row(pn.panel(bs, width=100), pn.indicators.Progress(width=300, value=10+i*10, bar_color=bs))
        for i, bs in enumerate(pn.indicators.Progress.param.bar_color.objects)
])
running
```

### Controls

The `Progress` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(progress.controls(jslink=True), progress, indeterminate.controls(jslink=True), indeterminate)
```

---
