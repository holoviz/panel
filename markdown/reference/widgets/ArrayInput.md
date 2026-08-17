# ArrayInput
---
```python
import numpy as np
import panel as pn

pn.extension()
```

The ``ArrayInput`` widget allows rendering and editing NumPy arrays using a text entry box whose contents are then parsed in Python. In order to avoid issues with large arrays the `ArrayInput` defines a `max_array_size`, if the array exceeds this size the textual representation will be summarized and editing will be disabled.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

##### Core

* **``max_array_size``** (int): Arrays larger than this limit will be allowed in Python but will not be serialized into JavaScript. Although such large arrays will thus not be editable in the widget, such a restriction helps avoid overwhelming the browser and lets other widgets remain usable.
* **``value``**: Parsed value of the indicated type

##### Display

* **``disabled``** (boolean): Whether the widget is editable
* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``placeholder``** (str): A placeholder string displayed when no value is entered

___

```python
array_input = pn.widgets.ArrayInput(label='Array Input ', value=np.random.randint(0, 10, (10, 2)))
array_input
```

``ArrayInput.value`` returns a value of the evaluated type that can be read out and set like other widgets:

```python
array_input.value
```

### Controls

The `ArrayInput` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(array_input.controls(jslink=True), array_input)
```

---
