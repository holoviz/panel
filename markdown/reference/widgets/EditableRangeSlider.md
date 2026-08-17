# EditableRangeSlider
---
```python
import math
import panel as pn
pn.extension()
```

The ``EditableRangeSlider`` widget allows selecting a floating-point range using a slider with two handles and for more precise control also offers a number input boxes.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``start``** (float): The lower bound for the slider, can be overridden by a lower `value`.
* **``end``** (float): The upper bound for the slider, can be overridden by a higher `value`.
* **``fixed_start``** (float | None): A fixed lower bound for the slider and input, `value` cannot exceed this.
* **``fixed_end``** (float | None): A fixed upper bound for the slider and input, `value` cannot exceed this.
* **``step``** (float): The interval between values
* **``value``** (tuple): Tuple of upper and lower bounds of selected range
* **``value_throttled``** (tuple): Tuple of upper and lower bounds of selected range throttled until mouseup

##### Display

* **``bar_color``** (color): Color of the slider bar as a hexadecimal RGB value
* **``direction``** (str): Whether the slider should go from left to right ('ltr') or right to left ('rtl')
* **``disabled``** (boolean): Whether the widget is editable
* **``format``** (str, bokeh.models.TickFormatter): Formatter to apply to the slider value
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``orientation``** (str): Whether the slider should be displayed in a 'horizontal' or 'vertical' orientation.
* **``tooltips``** (boolean): Whether to display tooltips on the slider handle

___

```python
range_slider = pn.widgets.EditableRangeSlider(
    label='Range Slider', start=0, end=math.pi, value=(math.pi/4., math.pi/2.),
    step=0.01)

range_slider
```

Here the `value` has no bounds and can exceed `end` and go below `start`. If `value` should be fixed to a certain range it can be set with `fixed_start` and `fixed_end`:

```python
range_slider.fixed_start = -1
```

The `value` of the widget returns a tuple of float values that can be read out and set like other widgets:

```python
range_slider.value
```

A custom format string or bokeh TickFormatter may be used to format the slider values:

```python
from bokeh.models.formatters import PrintfTickFormatter

str_format = pn.widgets.EditableRangeSlider(label='Distance', format='0.0a', start=100000, end=1000000)

tick_format = pn.widgets.EditableRangeSlider(label='Distance', format=PrintfTickFormatter(format='%.3f m'))

pn.Column(str_format, tick_format)
```

### Controls

Since the `EditableRangeSlider` widget is a composite widget its options can only be controlled from Python. Try out the effect of these parameters interactively:

```python
pn.Row(range_slider.controls(jslink=False), range_slider)
```

---
