# CheckButtonGroup
---
```python
import panel as pn
pn.extension()
```

The ``CheckButtonGroup`` widget allows selecting between a list of options by toggling the corresponding buttons. It falls into the broad category of multi-option selection widgets that provide a compatible API and include the ```MultiSelect```, ```CrossSelector``` and ```CheckBoxGroup``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): List or dictionary of options
* **``value``** (boolean): Currently selected options

##### Display

* **``color``** (str): A button theme should be one of ``'default'`` (white), ``'primary'`` (blue), ``'success'`` (green), ``'info'`` (yellow), or ``'danger'`` (red)
* **``description``** (str | Bokeh Tooltip | pn.widgets.TooltipIcon): A description which is shown when the widget is hovered.
* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``orientation``** (str, default='horizontal'): Button group orientation, either 'horizontal' or 'vertical'

___

```python
checkbutton_group = pn.widgets.CheckButtonGroup(label='Check Button Group', value=['Apple', 'Pear'], options=['Apple', 'Banana', 'Pear', 'Strawberry'])

checkbutton_group
```

``CheckButtonGroup.value`` returns a list of the currently selected options:

```python
checkbutton_group.value
```

### Styles

The color of the button can be set by selecting one of the available `color` values and the `variant` can be `'solid'` or `'outline'`:

```python
pn.Row(
    *(pn.Column(*(
        pn.widgets.CheckButtonGroup(
            label=p, color=p, variant=bs, options=['Foo', 'Bar', 'Baz'], value=['Bar']
        )
        for p in pn.widgets.Button.param.color.objects
    ))
    for bs in pn.widgets.Button.param.variant.objects)
)
```

### Controls

The `CheckButtonGroup` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(checkbutton_group.controls(jslink=True), checkbutton_group)
```

---
