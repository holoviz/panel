# DatetimeSlider
---
```python
import datetime as dt
import panel as pn

pn.extension()
```

The ``DatetimeSlider`` widget allows selecting a datetime value within a set bounds using a slider.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``start``** (date or datetime): The range's lower bound
* **``end``** (date or datetime): The range's upper bound
* **``value``** (date or datetime): The selected value as a datetime type
* **``value_throttled``** (datetime): The selected value as a datetime type throttled until mouseup
* **``step``** (number): The selected step of the slider in seconds, default is 1 minutes, i.e 60 seconds

##### Display

* **``bar_color``** (color): Color of the slider bar as a hexadecimal RGB value
* **``direction``** (str): Whether the slider should go from left to right ('ltr') or right to left ('rtl')
* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``orientation``** (str): Whether the slider should be displayed in a 'horizontal' or 'vertical' orientation.
* **``tooltips``** (boolean): Whether to display tooltips on the slider handle
* **``format``** (string): The datetime's format

___

```python
datetime_slider = pn.widgets.DatetimeSlider(label='Datetime Slider', start=dt.datetime(2019, 1, 1), end=dt.datetime(2019, 6, 1), value=dt.datetime(2019, 2, 8, 15, 40, 30))

datetime_slider
```

``DatetimeSlider.value`` returns a datetime type that can be read out or set like other widgets:

```python
datetime_slider.value
```

### Controls

The `DatetimeSlider` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(datetime_slider.controls(jslink=True), datetime_slider)
```

---
