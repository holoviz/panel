# Apply a Design

This guide addresses how to select a design system to apply to the components to achieve a consistent design language.

:::{versionadded} 1.0.0
The design feature was added in 1.0.0 and is actively being developed and improved.
:::

---

Applying different design systems in Panel can be achieved globally or per component. To select a `design` globally set it via the extension:

```{pyodide}
import panel as pn

pn.extension(design='fast')
```

Alternatively you can also explicitly import and set a `design` on the config:

```python
from panel.theme.fast import Fast

pn.config.design = Fast
```

Any component that is rendered will now inherit this design. However, alternatively we can also set a `design` explicitly on a particular component, e.g.:

```{pyodide}
from panel.theme.bootstrap import Bootstrap
from panel.theme.fast import Fast
from panel.theme.material import Material
from panel.theme.native import Native

pn.Tabs(
    ('Bootstrap', pn.widgets.FloatSlider(design=Bootstrap)),
    ('Fast', pn.widgets.FloatSlider(design=Fast)),
    ('Material', pn.widgets.FloatSlider(design=Material)),
    ('Native', pn.widgets.FloatSlider(design=Native)),
)
```

## Related Resources

- Discover [how to toggle between themes](themes.md) next.
