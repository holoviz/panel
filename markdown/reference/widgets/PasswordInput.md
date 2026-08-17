# PasswordInput
---
```python
import panel as pn
pn.extension()
```

The ``PasswordInput`` allows entering any string using an obfuscated text input box.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (str): The current value updated when pressing `<enter>` key.
* **``value_input``** (str): The current value updated on every key press.

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``max_length``** (int): The maximum number of allowed characters.
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``placeholder``** (str): A placeholder string displayed when no value is entered

___

```python
password_input = pn.widgets.PasswordInput(label='Password', placeholder='Enter your password here...')
password_input
```

``PasswordInput.value`` returns a string type that can be read out and set like other widgets:

```python
password_input.value
```

### Controls

The `PasswordInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(password_input.controls(jslink=True), password_input)
```

---
