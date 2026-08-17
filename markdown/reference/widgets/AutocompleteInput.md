# AutocompleteInput
---
```python
import panel as pn
pn.extension()
```

The `AutocompleteInput` widget allows selecting a `value` from a list or dictionary of `options` by entering the value into an auto-completing text field. It falls into the broad category of single-value, option-selection widgets that provide a compatible API and include the `RadioBoxGroup`, `Select` and `DiscreteSlider` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): A list or dictionary of options to select from
* **`restrict`** (boolean, `default=True`): Set to False in order to allow users to enter text that is not present in the options list.
* **`search_strategy`** (str): Define how to search the list of completion strings. The default option `"starts_with"` means that the user's text must match the start of a completion string. Using `"includes"` means that the user's text can match any substring of a completion string.
* **`value`** (str): The current value updated when pressing <enter> key; must be one of the option values if restrict=True.
* **`value_input`** (str): The current value updated on every key press.
* **`case_sensitive`** (boolean, `default=True`): Enable or disable case sensitivity for matching completions.

##### Display

* **`disabled`** (boolean): Whether the widget is editable
* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.
* **`placeholder`** (str): A placeholder string displayed when no option is selected
* **`min_characters`** (int, `default=2`): The number of characters a user must type before completions are presented.

___

```python
autocomplete = pn.widgets.AutocompleteInput(
    label='Autocomplete Input', options=['Biology', 'Chemistry', 'Physics'],
    case_sensitive=False, search_strategy='includes',
    placeholder='Write something here')

pn.Row(autocomplete, height=100)
```

Like most other widgets, `AutocompleteInput` has a value parameter that can be accessed or set:

```python
autocomplete.value
```

If `restrict=False` the `AutocompleteInput` will allow any input in addition to the completions it offers:

```python
not_restricted = autocomplete.clone(value='Mathematics', restrict=False)
pn.Row(not_restricted, height=100)
```

```python
not_restricted.value
```

The `options` parameter also accepts a dictionary whose keys are going to be the labels of the dropdown menu.

```python
dict_autocomplete = pn.widgets.AutocompleteInput(label='Autocomplete', options={'Biology': 1, 'Chemistry': 2})

pn.Row(dict_autocomplete, height=100)
```

```python
dict_autocomplete.value
```

Updating the value will display the right label.

```python
dict_autocomplete.value = 2
```

### Controls

The `AutocompleteInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(autocomplete.controls(jslink=True), autocomplete)
```

---
