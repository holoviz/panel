# RangeSlider
---
```python
import math
import panel as pn
pn.extension()
```

The ``RangeSlider`` widget allows selecting a floating-point range using a slider with two handles.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``start``** (float): The range's lower bound
* **``end``** (float): The range's upper bound
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
range_slider = pn.widgets.RangeSlider(
    label='Range Slider', start=0, end=math.pi, value=(math.pi/4., math.pi/2.), step=0.01)

range_slider
```

``RangeSlider.value`` returns a tuple of float values that can be read out and set like other widgets:

```python
range_slider.value
```

A custom format string or bokeh TickFormatter may be used to format the slider values:

```python
from bokeh.models.formatters import PrintfTickFormatter

str_format = pn.widgets.RangeSlider(label='Distance', format='0.0a', start=100000, end=1000000)

tick_format = pn.widgets.RangeSlider(label='Distance', format=PrintfTickFormatter(format='%.3f m'))

pn.Column(str_format, tick_format)
```

### Controls

The `RangeSlider` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(range_slider.controls(jslink=True), range_slider)
```

---
