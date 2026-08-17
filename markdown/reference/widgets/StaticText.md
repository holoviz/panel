# StaticText
---
```python
import panel as pn
pn.extension()
```

The ``StaticText`` widget displays a text value but does not allow editing it.

Discover more on using widgets to add interactivity to your applications in the [how-to guides on interactivity](../../how_to/interactivity/index.md). Alternatively, learn [how to set up callbacks and (JS-)links between parameters](../../how_to/links/index.md) or [how to use them as part of declarative UIs with Param](../../how_to/param/index.md).

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``label``** (str): The title of the widget
* **``name``** (str): Deprecated alias for ``label``; use ``label`` instead.
* **``value``** (str): Parsed datetime value

___

```python
static_text = pn.widgets.StaticText(label='Static Text', value='A string')

static_text
```

``StaticText.value`` returns a string that can be read out but cannot be set like other widgets:

```python
static_text.value
```

### Controls

The `StaticText` widget exposes a number of options which can be changed from both Python and Javascript. Try out the effect of these parameters interactively:

```python
pn.Row(static_text.controls(jslink=True), static_text)
```

---
