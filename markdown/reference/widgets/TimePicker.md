# TimePicker
---
```python
import datetime as dt
import panel as pn

pn.extension()
```

The ``TimePicker`` widget allows entering a time value as text or `datetime.time`.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (str | datetime.time): The current value
* **``start``** (str | datetime.time): Inclusive lower bound of the allowed time selection
* **``end``** (str | datetime.time): Inclusive upper bound of the allowed time selection

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``format``** (str): Formatting specification for the display of the picked date.

    ```
    +---+------------------------------------+------------+
    | H | Hours (24 hours)                   | 00 to 23   |
    | h | Hours                              | 1 to 12    |
    | G | Hours, 2 digits with leading zeros | 1 to 12    |
    | i | Minutes                            | 00 to 59   |
    | S | Seconds, 2 digits                  | 00 to 59   |
    | s | Seconds                            | 0, 1 to 59 |
    | K | AM/PM                              | AM or PM   |
    +---+------------------------------------+------------+
    ```
    See also https://flatpickr.js.org/formatting/#date-formatting-tokens.

* **``hour_increment``** (int): Defines the granularity of hour value increments in the UI. Default is 1.
* **``minute_increment``** (int): Defines the granularity of minute value increments in the UI. Default is 1.
* **``second_increment``** (int): Defines the granularity of second value increments in the UI. Default is 1.
* **``seconds``** (bool): Allows to select seconds. By default, only hours and minutes are selectable, and AM/PM depending on the `clock` option. Default is False.
* **``clock``** (str): Whether to use 12 hour or 24 hour clock. Default is `'12h'`.
___

The `TimePicker` widget allows selecting a time of day.

```python
time_picker = pn.widgets.TimePicker(label='Time Picker', value=dt.datetime.now().time(), format='H:i K')
time_picker
```

Either `datetime.time` or `str` can be used as input and `TimePicker` can be bounded by a start and end time.

```python
time_picker = pn.widgets.TimePicker(label='Time Picker', value="08:28", start='00:00', end='12:00')
time_picker
```

---
