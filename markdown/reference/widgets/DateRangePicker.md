# DateRangePicker
---
```python
import datetime as dt

import panel as pn

pn.extension()
```

The `DateRangePicker` widget allows selecting a date range using a text box and the browser's date-picking utility.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`end`** (date): The latest selectable date
* **`start`** (date): The earliest selectable date
* **`value`** (tuple): Tuple of upper and lower bounds of the selected range expressed as date types

##### Display

* **`disabled`** (boolean): Whether the widget is editable
* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.
* **`disabled_dates`** (list): dates to make unavailable for selection; others will be available
* **`enabled_dates`** (list): dates to make available for selection; others will be unavailable

___

``DateRangePicker`` uses a browser-dependent calendar widget to select the date range:

```python
date_range_picker = pn.widgets.DateRangePicker(
    label='Date Range Picker', value=(dt.date(2020, 1, 1), dt.date(2020, 1, 10))
)

pn.Column(date_range_picker, height=400)
```

To ensure it is visible in a notebook we have placed it in a `Column` with a fixed height.

`DateRangePicker.value` returns a tuple of date values type that can be read out or set like other widgets:

```python
date_range_picker.value
```

### Controls

The `DateRangePicker` widget exposes a number of options which can be changed from both Python and Javascript. Try out
the effect of these parameters interactively:

```python
pn.Row(date_range_picker.controls(jslink=True), date_range_picker)
```

---
