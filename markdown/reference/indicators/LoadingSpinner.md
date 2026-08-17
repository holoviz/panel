# LoadingSpinner
---
```python
import panel as pn

pn.extension()
```

The ``LoadingSpinner`` is a boolean indicator providing a visual representation of the loading status. If the `value` is set to `True` the spinner will rotate while setting it to `False` will disable the rotating segment.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``bgcolor``** (str): The color of spinner background segment, either 'light' or 'dark'
* **``color``** (str): The color of the spinning segment, one of 'primary', 'secondary', 'success', 'info', 'warn', 'danger', 'light', 'dark'
* **``name``** (str): A label to display alongside the spinner.
* **``size``** (int): The size of the spinner in pixels.
* **``value``** (boolean): Whether the indicator is spinning or not.

___

The `LoadingSpinner` can be instantiated in a spinning or idle state:

```python
idle = pn.indicators.LoadingSpinner(value=False, label='Idle...')
loading = pn.indicators.LoadingSpinner(value=True, size=20, label='Loading...')

pn.Row(idle, loading)
```

The `LoadingSpinner` indicator also supports a range of spinner colors and backgrounds:

```python
grid = pn.GridBox('', 'light', 'dark', ncols=3)

for color in pn.indicators.LoadingSpinner.param.color.objects:
    dark = pn.indicators.LoadingSpinner(size=50, value=True, color=color, bgcolor='dark')
    light = pn.indicators.LoadingSpinner(size=50, value=True, color=color, bgcolor='light')
    grid.extend((color, light, dark))

grid
```

---
