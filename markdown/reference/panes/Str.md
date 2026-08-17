# Str
---
```python
import panel as pn

pn.extension()
```

The ``Str`` pane allows rendering arbitrary text in a panel.

Unlike ```Markdown``` and ```HTML``` panes, a ``Str`` pane is interpreted as a raw string without applying any markup and is displayed in a fixed-width font by default.

The pane will render any text, and if given an `object` will display the `object`'s Python `repr`.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``object``** (str or object): The string to display. If a non-string type is supplied, the `repr` of that object is displayed.
* **``styles``** (dict): Dictionary specifying CSS styles

___

```python
str_pane = pn.pane.Str(
    'This is a raw string which will not be formatted in any way except for the applied style.',
    styles={'font-size': '12pt'}
)

str_pane
```

Like other panes the ``Str`` pane can be updated by setting its ``object`` parameter.  As mentioned above, non-string types are automatically cast to a string:

```python
str_pane.object = 1.3234232
```

Lets change the `object` back to its initial value:

```python
str_pane.object = 'This is a raw string which will not be formatted in any way except for the applied style.'
```

---
