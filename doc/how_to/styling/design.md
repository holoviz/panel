# Apply a Design

This guide addresses how to select a design system to apply to the components to achieve a consistent design language.

:::{versionadded} 1.0.0
The design feature was added in 1.0.0 and is actively being developed and improved.
:::

---

Applying different design systems in Panel can be achieved globally or per component. To select a `design` globally set it via the extension:

```{pyodide}
import panel as pn

pn.extension(design='material')
```

Alternatively you can also explicitly import and set a `design` on the config:

```python
from panel.theme import Material

pn.config.design = Material
```

Any component that is rendered will now inherit this design. However, alternatively we can also set a `design` explicitly on a particular component, e.g.:

```{pyodide}
from panel.theme import Bootstrap, Material, Native

def create_components(design):
    return pn.Column(
        pn.widgets.FloatSlider(name='Slider', design=design),
        pn.widgets.TextInput(name='TextInput', design=design),
        pn.widgets.Select(
            name='Select', options=['Biology', 'Chemistry', 'Physics'], design=design
        ),
        pn.widgets.Button(
            name='Click me!', icon='hand-click', button_type='primary', design=design
        )
    )

pn.Tabs(
    ('Bootstrap', create_components(Bootstrap)),
    ('Material', create_components(Material)),
    ('Native', create_components(Native)),
)
```

## Related Resources

- Discover [how to customize a design](design_variables.md) next.
- Discover [how to toggle between themes](themes.md) next.
