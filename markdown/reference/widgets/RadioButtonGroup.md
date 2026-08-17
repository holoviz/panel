# RadioButtonGroup
---
```python
import panel as pn
pn.extension()
```

The ``RadioButtonGroup`` widget allows selecting from a list or dictionary of values using a set of toggle buttons. It falls into the broad category of single-value, option-selection widgets that provide a compatible API and include the ```RadioBoxGroup```, ```Select```, and ```DiscreteSlider``` widgets.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``options``** (list or dict): A list or dictionary of options to select from
* **``value``** (object): The current value; must be one of the option values

##### Display

* **`variant`** (str): The button style, either 'solid' or 'outline'.
* **``color``** (str): A button theme should be one of ``'default'`` (white), ``'primary'`` (blue), ``'success'`` (green), ``'info'`` (yellow), or ``'danger'`` (red)
* **``description``** (str | Bokeh Tooltip | pn.widgets.TooltipIcon): A description which is shown when the widget is hovered.
* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``orientation``** (str, default='horizontal'): Button group orientation, either 'horizontal' or 'vertical'.

___

```python
radio_group = pn.widgets.RadioButtonGroup(
    label='Radio Button Group', options=['Biology', 'Chemistry', 'Physics'], color='success')

radio_group
```

Like most other widgets, ``RadioButtonGroup`` has a value parameter that can be accessed or set:

```python
radio_group.value
```

### Styles

The color of the buttons can be set by selecting one of the available `color` values and the `variant` can be `'solid'` or `'outline'`:

```python
pn.Row(
    *(pn.Column(*(
        pn.widgets.RadioButtonGroup(
            label=p, color=p, variant=bs, options=['Foo', 'Bar', 'Baz'], value='Bar'
        )
        for p in pn.widgets.Button.param.color.objects
    ))
    for bs in pn.widgets.Button.param.variant.objects)
)
```

### Controls

The `RadioButtonGroup` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(radio_group.controls(jslink=True), radio_group)
```

---
