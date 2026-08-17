# DateRangeSlider
---
```python
import datetime as dt
import panel as pn

pn.extension()
```

The ``DateRangeSlider`` widget allows selecting a date range using a slider with two handles.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``start``** (datetime): The range's lower bound
* **``end``** (datetime): The range's upper bound
* **``step``** (int): Step in days
* **``value``** (tuple): Tuple of upper and lower bounds of the selected range expressed as datetime types
* **``value_throttled``** (tuple): Tuple of upper and lower bounds of the selected range expressed as datetime types throttled until mouseup

##### Display

* **``bar_color``** (color): Color of the slider bar as a hexadecimal RGB value
* **``direction``** (str): Whether the slider should go from left to right ('ltr') or right to left ('rtl')
* **``disabled``** (boolean): Whether the widget is editable
* **``format``** (str): Formatter to apply to the slider value
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``orientation``** (str): Whether the slider should be displayed in a 'horizontal' or 'vertical' orientation.
* **``tooltips``** (boolean): Whether to display tooltips on the slider handle
* **``format``** (str): The datetime format

___

The slider start and end can be adjusted by dragging the handles and whole range can be shifted by dragging the selected range.

```python
date_range_slider = pn.widgets.DateRangeSlider(
    label='Date Range Slider',
    start=dt.datetime(2017, 1, 1), end=dt.datetime(2019, 1, 1),
    value=(dt.datetime(2017, 1, 1), dt.datetime(2018, 1, 10)),
    step=2
)

date_range_slider
```

``DateRangeSlider.value`` returns a tuple of datetime values that can be read out and set like other widgets:

```python
date_range_slider.value
```

A custom format string may be used to format the slider values:

```python
str_format = pn.widgets.DateRangeSlider(
    label='Date Range Slider',
    start=dt.datetime(2017, 1, 1), end=dt.datetime(2019, 1, 1),
    value=(dt.datetime(2017, 1, 1), dt.datetime(2018, 1, 10)),
    step=2,
    format='%Y-%m-%d'
)
str_format
```

### Controls

The `DateRangeSlider` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(date_range_slider.controls(jslink=True), date_range_slider)
```

---
