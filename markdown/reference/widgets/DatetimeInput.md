# DatetimeInput
---
```python
import datetime as dt
import panel as pn

pn.extension()
```

The ``DatetimeInput`` widget allows entering a datetime value as text and parsing it using a pre-defined formatter.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``start``** (datetime): Lower bound
* **``end``** (datetime): Upper bound
* **``value``** (datetime): Parsed datetime value

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``format``** (str): Datetime formatting string that determines how the value is formatted and parsed (``default='%Y-%m-%d %H:%M:%S'``)
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The datetime parser uses the defined ``format`` to validate the input value, if the entered text is not a valid datetime a warning will be shown in the title as "`(invalid)`":

```python
dt_input = pn.widgets.DatetimeInput(label='Datetime Input', value=dt.datetime(2019, 2, 8))

dt_input
```

``DatetimeInput.value`` returns a datetime object and can be accessed and set like other widgets:

```python
dt_input.value
```

### Controls

The `DateTimeInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(dt_input.controls(jslink=True), dt_input)
```

---
