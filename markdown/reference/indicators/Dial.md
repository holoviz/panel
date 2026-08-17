# Dial
---
```python
import panel as pn

pn.extension()
```

The ``Dial`` is a value indicator providing a visual representation of a value as a simple radial dial.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``annulus_width``** (int, default=10): Width of the gauge annulus.
* **``bounds``** (tuple, default=(0, 100)): The upper and lower bound of the dial.
* **``colors``** (list): Color thresholds for the Gauge, specified as a list of tuples of the fractional threshold and the color to switch to.
* **``default_color``** (str, default='lightblue'): Color to use if no color threshold are supplied to the `color` parameter
* **``end_angle``** (float or int, default=-45) Angle at which the gauge ends.
* **``format``** str(str, default='{value}%'): Formatting string for the value indicator.
* **``nan_format``** str(str, default='-'): How to format nan values.
* **``needle_color``** (str, default='black): Color of the needle.
* **``needle_width``** (float, default=0.1): Radial width of needle in radians.
* **``start_angle``** (float or int, default=225): Angle at which the gauge starts.
* **``tick_size``** (int): Font size of the tick labels.
* **``title_size``** (int): Font size of the title.
* **``unfilled_color``** (str, default='whitesmoke'): Color of the unfilled region of the Dial
* **``value``** (float or int, default=25): Value to indicate on the dial a value within the declared bounds.
* **``value_size``** (str): Font size of value label.

___

The simplest form of a Gauge just requires setting a `value` which must be within the `bounds`. The default formatter and bounds assume you are providing a percentage:

```python
pn.indicators.Dial(label='Failure Rate', value=10, bounds=(0, 100))
```

If we want to display some other value such as the revolutions per minute of an engine we can set a different `bounds` value and override the `format`. Additionally we may also provide a different set of colors defining the threshold points at which the color should change as a fraction of the provided bounds. The `colors` accepts a list of tuples defining the fractions and the color:

```python
pn.indicators.Dial(
    label='Engine', value=2500, bounds=(0, 3000), format='{value} rpm',
    colors=[(0.2, 'green'), (0.8, 'gold'), (1, 'red')]
)
```

---
