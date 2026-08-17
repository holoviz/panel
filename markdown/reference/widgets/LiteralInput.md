# LiteralInput
---
```python
import panel as pn
pn.extension()
```

The ``LiteralInput`` widget allows entering any Python literal using a text entry box whose contents are then parsed in Python. The widget only supports Python literal types. Optionally a ``type`` may be declared to validate the literal before updating the parameter.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``serializer``** (str['ast', 'json]): The serialization (and deserialization) method to use. 'ast' uses `ast.literal_eval` and 'json' uses `json.loads` and `json.dumps`.
* **``type``** (type or tuple(type)): A Python literal type (e.g. list, dict, set, int, float, bool, str)
* **``value``**: Parsed value of the indicated type

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``placeholder``** (str): A placeholder string displayed when no value is entered

___

```python
literal_input = pn.widgets.LiteralInput(label='Literal Input (dict)', value={'key': [1, 2, 3]}, type=dict)
literal_input
```

``LiteralInput.value`` returns a value of the evaluated type that can be read out and set like other widgets:

```python
literal_input.value
```

### Controls

The `LiteralInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(literal_input.controls(jslink=True), literal_input)
```

---
