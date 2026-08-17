# DatetimeRangeInput
---
```python
import datetime as dt
import panel as pn

pn.extension()
```

The ``DatetimeRangeInput`` widget allows selecting a datetime range using two `DatetimeInput` widgets, which return a tuple range.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``format``** (str): Datetime formatting string that determines how the value is formatted and parsed (``default='%Y-%m-%d %H:%M:%S'``)
* **``start``** (datetime): The range's lower bound
* **``end``** (datetime): The range's upper bound
* **``value``** (tuple): Tuple of upper and lower bounds of the selected range expressed as datetime types

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The datetime parser uses the defined ``format`` to validate the input value, if the entered text is not a valid datetime a warning will be shown in the title as "`(invalid)`":

```python
datetime_range_input = pn.widgets.DatetimeRangeInput(
    label='Datetime Range Input',
    start=dt.datetime(2017, 1, 1), end=dt.datetime(2019, 1, 1),
    value=(dt.datetime(2017, 1, 1), dt.datetime(2018, 1, 10)),
    width=300
)

datetime_range_input
```

``DatetimeRangeInput.value`` returns a tuple of datetime values that can be read out and set like other widgets:

```python
datetime_range_input.value
```

### Controls

The `DatetimeRangeInput` widget is a composite widget, which requires Python for communication. Therefore the controls only work when connected in a live Python server/kernel:

```python
pn.Row(datetime_range_input.controls(jslink=False), datetime_range_input)
```

---
