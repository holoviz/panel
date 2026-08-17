# TextInput
---
```python
import panel as pn
pn.extension()
```

The ``TextInput`` allows entering any string using a text input box.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (str): The current value updated when pressing the `<enter>` key or when the widget loses focus because the user clicks away or presses the tab key.
* **``value_input``** (str): The current value updated on every key press.
* **``enter_pressed``** (event): An event that triggers when the `<enter>` key is pressed.

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``max_length``** (int): Max character length of the input field. Defaults to 5000
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``placeholder``** (str): A placeholder string displayed when no value is entered

___

```python
text_input = pn.widgets.TextInput(label='Text Input', placeholder='Enter a string here...')
text_input
```

``TextInput.value`` returns a string type that can be read out and set like other widgets:

```python
text_input.value
```

### Controls

The `TextInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(text_input.controls(jslink=True), text_input)
```

---
