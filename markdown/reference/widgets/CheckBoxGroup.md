# CheckBoxGroup
---
```python
import panel as pn

pn.extension()
```

The ``CheckBoxGroup`` widget allows selecting between a list of options by ticking the corresponding checkboxes. It falls into the broad category of multi-option selection widgets that provide a compatible API and include the ```MultiSelect```, ```CrossSelector``` and ```CheckButtonGroup``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): List or dictionary of options
* **``value``** (list): Currently selected options

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``inline``** (boolean): Whether to arrange the items vertically in a column (``False``) or horizontally in a line (``True``)
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
checkbox_group = pn.widgets.CheckBoxGroup(
    label='Checkbox Group', value=['Apple', 'Pear'], options=['Apple', 'Banana', 'Pear', 'Strawberry'],
    inline=True)

checkbox_group
```

``CheckBoxGroup.value`` returns a list of the currently selected options:

```python
checkbox_group.value
```

### Controls

The `CheckboxBoxGroup` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(checkbox_group.controls(jslink=True), checkbox_group)
```

---
