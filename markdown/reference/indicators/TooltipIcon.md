# TooltipIcon
---
```python
import panel as pn

pn.extension()
```

The ``TooltipIcon`` is a tooltip indicator providing a Tooltip. The `value` will be the text inside of the tooltip.

#### Parameters:

For details on other options for customizing the component see the [layout](../../how_to/layout/index.md) and [styling](../../how_to/styling/index.md) how-to guides.

* **``value``** (`str` or `bokeh.models.Tooltip`): The text inside the tooltip.

___

The `TooltipIcon` indicator can be instantiated with either a string:

```python
pn.widgets.TooltipIcon(value="This is a simple tooltip by using a string")

```

or as a `bokeh.models.Tooltip`:

```python
from bokeh.models import Tooltip

pn.widgets.TooltipIcon(value=Tooltip(content="This is a tooltip using a bokeh.models.Tooltip", position="right"))

```

The `TooltipIcon` can be used to add more information to a widgets:

```python
pn.Row(
    pn.widgets.Button(label="Click me!"), 
    pn.widgets.TooltipIcon(value="Nothing happens when you click the button!")
)
```

---
