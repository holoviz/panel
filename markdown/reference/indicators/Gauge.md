# Gauge
---
```python
import panel as pn

pn.extension('echarts')
```

The ``Gauge`` is a value indicator providing a visual representation of a value as a gauge or speed-o-meter. The `Gauge` is rendered using the ECharts library so when working in the notebook, ensure you load 'echarts' in `pn.extension`.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``annulus_width``** (int, default=10): Width of the gauge annulus.
* **``bounds``** (tuple, default=(0, 100)): The upper and lower bound of the dial.
* **``colors``** (list): Color thresholds for the Gauge, specified as a list of tuples of the fractional threshold and the color to switch to.
* **``custom_opts``** (dict): Additional options to pass to the ECharts Gauge definition.
* **``end_angle``** (float or int, default=-45) Angle at which the gauge ends.
* **``format``** str(str, default='{value}%'): Formatting string for the value indicator.
* **``num_splits``** (int, default=10): Number of splits along the gauge.
* **``show_ticks``** (boolean, default=True): Whether to show ticks along the dials.
* **``show_labels``** (boolean, default=True): Whether to show tick labels along the dials.
* **``start_angle``** (float or int, default=225): Angle at which the gauge starts.
* **``tooltip_format``** (str, default='{b} : {c}%'): Formatting string for the hover tooltip.
* **``title_size``** (int, default=18): Size of title font.
* **``value``** (float or int, default=25): Value to indicate on the gauge a value within the declared bounds.

___

The simplest form of a Gauge just requires setting a `value` which must be within the `bounds`. The default formatter and bounds assume you are providing a percentage:

```python
pn.indicators.Gauge(label='Failure Rate', value=10, bounds=(0, 100))
```

If we want to display some other value such as the revolutions per minute of an engine we can set a different `bounds` value and override the `format`. Additionally we may also provide a different set of colors defining the threshold points at which the color should change as a fraction of the provided bounds. The `colors` accepts a list of tuples defining the fractions and the color:

```python
pn.indicators.Gauge(
    label='Engine', value=2500, bounds=(0, 3000), format='{value} rpm',
    colors=[(0.2, 'green'), (0.8, 'gold'), (1, 'red')]
)
```

You can also change the color of the needle by passing custom options:

```python
pn.indicators.Gauge(
    label="Engine", value=2500, bounds=(0, 3000), format='{value} rpm',
    colors=[(0.2, 'green'), (0.8, 'gold'), (1, 'red')],
    custom_opts={"pointer": {"itemStyle": {"color": 'red'}}}
)

```

---
