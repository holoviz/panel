# LinearGauge
---
```python
import panel as pn

pn.extension()
```

The ``LinearGauge`` is a value indicator providing a visual representation of a value in a certain range as a simple linear gauge. It is similar to `Dial` and `Gauge` elements but visually more compact.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``bounds``** (tuple, default=(0, 100)): The upper and lower bound of the dial.
* **``colors``** (list): Color thresholds for the gauge, specified as a list of evenly spaced colors or  tuples of the fractional threshold and the color to switch to.
* **``default_color``** (str, default='lightblue'): Color to use if no color threshold are supplied to the `color` parameter
* **``format``** str(str, default='{value}%'): Formatting string for the value indicator.
* **``nan_format``** str(str, default='-'): How to format nan values.
* **``needle_color``** (str, default='black): Color of the needle.
* **``show_boundaries``** (boolean, default=False): Whether to show transitions between colors.
* **``tick_size``** (int): Font size of the tick labels.
* **``title_size``** (int): Font size of the title.
* **``unfilled_color``** (str, default='whitesmoke'): Color of the unfilled region of the LinearGauge
* **``value``** (float or int, default=25): Value to indicate on the dial a value within the declared bounds.
* **``value_size``** (str): Font size of value label.

___

The simplest form of a `LinearGauge` just requires setting a `value` which must be within the `bounds`. The default formatter and bounds assume you are providing a percentage:

```python
pn.indicators.LinearGauge(label='Failure Rate', value=30, bounds=(0, 100))
```

If we want to display some other value such as the revolutions per minute of an engine we can set a different `bounds` value and override the `format`. Additionally we may also provide a different set of colors defining the threshold points at which the color should change as a fraction of the provided bounds. The `colors` accepts a list of tuples defining the fractions and the color:

```python
pn.indicators.LinearGauge(
    label='Engine', value=2500, bounds=(0, 3000), format='{value:.0f} rpm',
    colors=['green', 'gold', 'red'], horizontal=True, width=125
)
```

If we want to show the transition points between the different colors we can also enable `show_boundaries`:

```python
pn.indicators.LinearGauge(
    label='Engine', value=2800, bounds=(0, 3000), format='{value:.0f} rpm',
    colors=[(0.2, 'green'), (0.8, 'gold'), (1, 'red')], show_boundaries=True
)
```

---
