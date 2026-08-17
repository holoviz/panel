# TextAreaInput
---
```python
import panel as pn
pn.extension()
```

The ``TextAreaInput`` allows entering any multiline string using a text input box. Lines are joined with the newline character ``\n``.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``value``** (str): The current value updated when the widget loses focus because the user clicks away or presses the tab key.
* **``value_input``** (str): The current value updated on every key press.

##### Display

* **`auto_grow`** (boolean, default=False): Whether the TextArea should automatically grow in height to fit the content.
* **`cols`** (int, default=2): The number of columns in the text input field.
* **`disabled`** (boolean, default=False): Whether the widget is editable
* **`max_length`** (int, default=5000): Max character length of the input field. Defaults to 5000
* **`max_rows`** (int, default=None): The maximum number of rows in the text input field when `auto_grow=True`.
* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.
* **`placeholder`** (str): A placeholder string displayed when no value is entered
* **`rows`** (int, default=2): The number of rows in the text input field.
* **`resizable`** (boolean | str, default='both'): Whether the layout is interactively resizable, and if so in which dimensions: `width`, `height`, or `both`.

___

```python
text_area_input = pn.widgets.TextAreaInput(label='Text Area Input', placeholder='Enter a string here...')
text_area_input
```

``TextAreaInput.value`` returns a string type that can be read out and set like other widgets:

```python
text_area_input.value
```

An auto-growing `TextAreaInput` will grow (and shrink) in height to accommodate the entered text. Setting `rows` together with `auto_grow` will set a lower bound on the number of rows and setting `max_rows` will provide an upper bound:

```python
pn.widgets.TextAreaInput(label='Growing TextArea', auto_grow=True, max_rows=10, rows=6, value="""\
This text area will grow when newlines are added to the text:

1. Foo
2. Bar
3. Baz
""", width=500)
```

If you only want the text area to be resizable in the vertical direction, you can set the resizeable parameter to 'height':

```python
pn.widgets.TextAreaInput(label="Vertical Adjustable TextArea", resizable="height")
```

### Controls

The `TextAreaInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(text_area_input.controls(jslink=True), text_area_input)
```

---
