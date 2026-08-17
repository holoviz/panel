# RadioBoxGroup
---
```python
import panel as pn
pn.extension()
```

The ``RadioBoxGroup`` widget allows selecting from a list or dictionary of values using a set of checkboxes. It falls into the broad category of single-value, option-selection widgets that provide a compatible API and include the ```RadioButtonGroup```, ```Select``` and ```DiscreteSlider``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): A list or dictionary of options to select from
* **``value``** (object): The current value; must be one of the option values

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``inline``** (boolean): Whether to arrange the items vertically in a column (``False``) or horizontally in a line (``True``)
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
radio_group = pn.widgets.RadioBoxGroup(label='RadioBoxGroup', options=['Biology', 'Chemistry', 'Physics'], inline=True)

radio_group
```

Like most other widgets, ``RadioBoxGroup`` has a value parameter that can be accessed or set:

```python
radio_group.value
```

### Controls

The `RadioBoxGroup` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(radio_group.controls(jslink=True), radio_group)
```

---
