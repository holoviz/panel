# CrossSelector
---
```python
import panel as pn

pn.extension()
```

The `CrossSelector` widget allows selecting multiple values from a list of options by moving items between two lists. It falls into the broad category of multi-option selection widgets that provide a compatible API and include the `MultiSelect`, `CheckBoxGroup` and `CheckButtonGroup` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **`definition_order`** (boolean, default=True): Whether to preserve definition order after filtering. Disable to allow the order of selection to define the order of the selected list.
* **`filter_fn`** (function): The function used for filtering the options when searching using the text fields. The supplied function must allow two arguments; the user supplied search pattern and the label from the list of supplied `options`. The default is `re.search`, which matches options using a standard regular expression.
* **`options`** (list or dict): List or dictionary of available options
* **`value`** (list): Currently selected options

##### Display

* **`disabled`** (boolean): Whether the widget is editable
* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

The `CrossSelector` is made up of a number of components:

* Two lists for the unselected (left) and selected (right) option values
* Filter boxes that allow using a regex to match options in the list of values below
* Buttons to move values from the unselected to the selected list (`>>`) and vice versa (`<<`)

```python
cross_selector = pn.widgets.CrossSelector(label='Fruits', value=['Apple', 'Pear'], 
    options=['Apple', 'Banana', 'Pear', 'Strawberry'])

cross_selector
```

`CrossSelector.value` returns a list of the currently selected options:

```python
cross_selector.value
```

---
