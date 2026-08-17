# JSONEditor
---
```python
import panel as pn
import param

pn.extension('ace', 'jsoneditor')
```

The ``JSONEditor`` widget provides a visual editor for JSON-serializable datastructures, e.g. Python dictionaries and lists, with functionality for different editing modes, inserting objects and validation using JSON Schema.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``disabled``** (boolean): Whether the editor is disabled (equivalent to setting `mode='view'`)
* **``menu``** (boolean): Adds main menu bar - Contains format, sort, transform, search etc. functionality. true by default. Applicable in all types of mode.
* **``mode``** (str): Sets the editor mode. In 'view' mode, the data and datastructure is read-only. In 'form' mode, only the value can be changed, the data structure is read-only. Mode 'code' requires the Ace editor to be loaded on the page. Mode 'text' shows the data as plain text. The 'preview' mode can handle large JSON documents up to 500 MiB. It shows a preview of the data, and allows to transform, sort, filter, format, or compact the data.
* **``search``** (boolean): Enables a search box in the upper right corner of the JSONEditor. true by default. Only applicable when mode is 'tree', 'view', or 'form'.
* **``schema``** (dict): Validate the JSON object against a JSON schema. A JSON schema describes the structure that a JSON object must have, like required properties or the type that a value must have. See http://json-schema.org/ for more information.
* **``value``** (str): The current JSON serializable datastructure to display and edit

##### Display

* **`label`** (str): The title of the widget
* **`name`** (str): Deprecated alias for ``label``; use ``label`` instead.

___

To construct a `JSONEditor` editor widget we simply give it a value to render:

```python
json_editor = pn.widgets.JSONEditor(value={
    'dict'  : {'key': 'value'},
    'float' : 3.14,
    'int'   : 1,
    'list'  : [1, 2, 3],
    'string': 'A string',
}, width=400)

json_editor
```

### Mode

The JSON Editor has a number of modes that provide different ways of viewing and editing the `JSONEditor.value`. Note that to enable support for `mode='code'` you must load 'ace' using `pn.extension('ace')`:

```python
pn.FlexBox(*(pn.Column(f'### Mode: {mode}', json_editor.clone(mode=mode)) for mode in pn.widgets.JSONEditor.param.mode.objects))
```

### Validation

The `JSONEditor` provides validation of the `value` by providing a JSON schema. A JSON schema describes the structure that a JSON object must have, like required properties or the type that a value must have. See http://json-schema.org/ for more information.

```python
pn.widgets.JSONEditor(
    schema={
      "title": "Person",
      "type": "object",
      "properties": {
        "firstName": {
          "type": "string",
          "description": "The person's first name."
        },
        "lastName": {
          "type": "string",
          "description": "The person's last name."
        },
        "age": {
          "description": "Age in years which must be equal to or greater than zero.",
          "type": "integer",
          "minimum": 0
        }
      }
    },
    value={
        'firstName': 2,
        'lastName': 'Smith',
        'age': 13.5
    }, height=500, width=400
)
```

### Controls

The `JSONEditor` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(json_editor.controls(jslink=True), json_editor)
```

---
