# MultiChoice
---
```python
import panel as pn
pn.extension()
```

The ``MultiChoice`` widget allows selecting multiple values from a list of options. It falls into the broad category of multi-value, option-selection widgets that provide a compatible API and include the ```MultiSelect```, ```CrossSelector```, ```CheckBoxGroup``` and ```CheckButtonGroup``` widgets. The ``MultiChoice`` widget provides a much more compact UI than ```MultiSelect```.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): List or dictionary of options
* **``max_items``** (int): Maximum number of options that can be selected
* **``value``** (list): Currently selected option values

##### Display

* **``delete_button``** (boolean): Whether to display a button to delete a selected option
* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``option_limit``** (int): Maximum number of options to display at once.
* **``search_option_limit``** (int): Maximum number of options to display at once if search string is entered.
* **``placeholder``** (str): String displayed when no selection has been made.
* **``solid``** (boolean): Whether to display widget with solid or light style.

___

```python
multi_choice = pn.widgets.MultiChoice(label='MultiSelect', value=['Apple', 'Pear'],
    options=['Apple', 'Banana', 'Pear', 'Strawberry'])

pn.Column(multi_choice, height=200)
```

``MultiChoice.value`` returns a list of the currently selected options:

```python
multi_choice.value
```

The `solid` option controls the style of the widget:

```python
pn.Column(multi_choice.clone(solid=False), height=200)
```

### Controls

The `MultiChoice` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(multi_choice.controls(jslink=True), multi_choice)
```

---
