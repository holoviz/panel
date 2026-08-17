# MultiSelect
---
```python
import panel as pn
pn.extension()
```

The ``MultiSelect`` widget allows selecting multiple values from a list of options. It falls into the broad category of multi-value, option-selection widgets that provide a compatible API and include the ```CrossSelector```, ```CheckBoxGroup``` and ```CheckButtonGroup``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): List or dictionary of options
* **``value``** (list): Currently selected option values

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

##### Events

* **``on_double_click``** (Callable[DoubleClickEvent, None]): Allows registering a callback that fires when an option is double clicked. The callback is given a `DoubleClickEvent` containing the clicked `option`.

___

```python
multi_select = pn.widgets.MultiSelect(label='MultiSelect', value=['Apple', 'Pear'],
    options=['Apple', 'Banana', 'Pear', 'Strawberry'], size=8)

multi_select
```

``MultiSelect.value`` returns a list of the currently selected options:

```python
multi_select.value
```

### Controls

The `MultiSelect` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(multi_select.controls(jslink=True), multi_select)
```

---
