# ColorPicker
---
```python
import panel as pn

pn.extension()
```

The ``ColorPicker`` widget allows selecting a color using the browser's color-picking widget support.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (color): A hexadecimal RGB color value

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.

___

When clicked the ``ColorPicker`` opens a browser-dependent color-picking widget:

```python
colorpicker = pn.widgets.ColorPicker(label='Color Picker', value='#99ef78')

colorpicker
```

``ColorPicker.value`` returns a hexadecimal RGB value:

```python
colorpicker.value
```

### Controls

The `ColorPicker` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(colorpicker.controls(jslink=True), colorpicker)
```

---
