# ToggleGroup
---
```python
import panel as pn
pn.extension()
```

A ``ToggleGroup`` is a group of widgets which can be switched 'on' or 'off'.

This widget is a thin wrapper for using either a `CheckButtonGroup`, `CheckBoxGroup`, `RadioButtonGroup` or `RadioBoxGroup` to select between a single or multiple given values.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``widget_type``** (str): Two types of widgets are available: ``button`` (default) and ``box``
* **``behavior``** (str): Two different behaviors are available: ``check`` (default) and ``radio``

As the `ToggleGroup` class is just a Factory for other different widget types, the above parameters cannot be changed or set after instantion.
All additional given parameters are passed through to the constructor of the resulting widget class.

The different parameter combinations and the resulting widget type are shown in the following table.

| widget_type | behavior  | Resulting Widget  |
|---|---|---|
| button  | check  |  `CheckButtonGroup` |
| button  | radio  |  `RadioButtonGroup` |
|  box | check  |  `CheckBoxGroup` |
| box  |  radio | `RadioBoxGroup`  |

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

```python
toggle_group = pn.widgets.ToggleGroup(label='ToggleGroup', options=['Biology', 'Chemistry', 'Physics'])

toggle_group
```

Like most other widgets, ``ToggleGroup`` has a value parameter that can be accessed or set:

```python
toggle_group.value
```

```python
toggle_group = pn.widgets.ToggleGroup(label='ToggleGroup', options=['Biology', 'Chemistry', 'Physics'], behavior="radio")

toggle_group
```

For radio behavior the value is only a single value!

```python
toggle_group.value
```

The resulting object is not of type ToggleGroup but is an object dependent of the input parameters as shown in the `Parameters` section

```python
type(toggle_group)
```

### Controls

The `ToggleGroup` widget (concretely the created, underlying widget) exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(toggle_group.controls(jslink=True), toggle_group)
```

---
