# DatePicker
---
```python
import datetime as dt

import panel as pn

pn.extension()
```

The ``DatePicker`` widget allows selecting selecting a date value using a text box and the browser's date-picking utility.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``end``** (datetime): The latest selectable date
* **``start``** (datetime): The earliest selectable date
* **``value``** (datetime): The selected value as a datetime type

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``disabled_dates``** (list): dates to make unavailable for selection; others will be available
* **``enabled_dates``** (list): dates to make available for selection; others will be unavailable

___

``DatePicker`` uses a browser-dependent calendar widget to select the date:

```python
date_picker = pn.widgets.DatePicker(label='Date Picker', value=dt.datetime(2024, 4, 1, 11, 37))

pn.Column(date_picker, height=400)
```

To ensure it is visible in a notebook we have placed it in a `Column` with a fixed height.

`DatePicker.value` returns a datetime type that can be read out or set like other widgets:

```python
date_picker.value
```

### Controls

The `DatePicker` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(date_picker.controls(jslink=True), date_picker)
```

---
