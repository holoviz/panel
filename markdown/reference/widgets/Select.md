# Select
---
```python
import panel as pn
pn.extension()
```

The ``Select`` widget allows selecting a ``value`` from a list or dictionary of ``options`` by selecting it from a dropdown menu or selection area. It falls into the broad category of single-value, option-selection widgets that provide a compatible API and include the ```RadioBoxGroup```, ```AutocompleteInput``` and ```DiscreteSlider``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): A list or dictionary of options to select from
* **``disabled_options``** (list): Optional list of ``options`` that are disabled, i.e. unusable and un-clickable. If ``options`` is a dictionary the list items must be dictionary values.
* **``groups``** (dict): A dictionary whose keys are used to visually group the options and whose values are either a list or a dictionary of options to select from. Mutually exclusive with ``options`` and valid only if ``size`` is 1.
* **``size``** (int, default=1): Declares how many options are displayed at the same time. If set to 1 displays options as dropdown otherwise displays scrollable area.
* **``value``** (object): The current value; must be one of the option values

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
select = pn.widgets.Select(label='Select', options=['Biology', 'Chemistry', 'Physics'])

select
```

Like most other widgets, ``Select`` has a value parameter that can be accessed or set:

```python
select.value
```

The `options` parameter also accepts a dictionary whose keys are going to be the labels of the dropdown menu.

```python
select = pn.widgets.Select(label='Select', options={'Biology': 1, 'Chemistry': 2})

select
```

```python
select.value
```

Updating the value will display the right label.

```python
select.value = 2
```

A subset of the displayed items can be disabled with `disabled_options`. The widget `value` cannot be set to one of the `disabled_options`, either programmatrically or with the user interface.

```python
select = pn.widgets.Select(label='Select', options=['Biology', 'Chemistry', 'Physics'], disabled_options=['Chemistry'])

select
```

The items displayed in the dropdown menu can be grouped visually (also known as *optgroup*) by setting the `groups` parameter **instead of** `options`. `groups` accepts a dictionary whose keys are used to group the options and whose values are defined similarly to how `options` are defined.

```python
select = pn.widgets.Select(label='Select', groups={'Europe': ['Greece', 'France'], 'Africa': ['Algeria', 'Congo']})

select
```

```python
select.value
```

Instead of a dropdown menu we can also select one option from a list by rendering multiple options at once using the `size` parameter:

```python
select_area = pn.widgets.Select(label='Select', options=['Biology', 'Chemistry', 'Physics'], size=2)

select_area
```

When `size` is set to a value greater than 1 the widget supports the `disabled_options` parameter but does not support `groups`.

```python
pn.widgets.Select(label='Select', options=['Biology', 'Chemistry', 'Physics'], size=2, disabled_options=['Chemistry'])
```

### Controls

The `Select` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(select.controls(jslink=True), select)
```

---
