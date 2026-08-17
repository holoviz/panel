# JSON
---
```python
import json
import panel as pn

pn.extension()
```

The ``JSON`` pane allows rendering arbitrary JSON strings, dicts and other json serializable objects in a panel.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``depth``** (int): Depth to which the JSON structure is expanded on initialization (`depth=-1` indicates full expansion)
* **``hover_preview``** (bool): Whether to enable hover preview for collapsed nodes
* **``object``** (str or object): JSON string or JSON serializable object
* **``theme``** (string): If no value is provided, it defaults to the current theme set by pn.config.theme, as specified in the JSON.THEME_CONFIGURATION dictionary. If not defined there, it falls back to the default parameter value ('light').

___

The `JSON` pane can be used to render a tree view of arbitrary JSON objects which may be defined as a string or a JSON-serializable Python object.

```python
json_obj = {
    'boolean': False,
    'dict': {'a': 1, 'b': 2, 'c': 3},
    'int': 1,
    'float': 3.1,
    'list': [1, 2, 3],
    'null': None,
    'string': 'A string',
}

json = pn.pane.JSON(json_obj, name='JSON')

json
```

### Controls

The `JSON` pane exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(json.controls(jslink=True), json)
```

---
