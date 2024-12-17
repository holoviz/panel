# Customize a Design

This guide addresses how to customize a design system with CSS variables.

:::{versionadded} 1.0.0
The design feature was added in 1.0.0 and is actively being developed and improved. Currently there are a limited number of design variables but in future the goal is to expose a large variety of styling options via CSS variables.
:::

```{admonition} Prerequisites
1. The [How-to > Apply a Design](./design) guides describe how to select a design system to apply to the components to achieve a consistent design language.
2. The [How-to > Apply CSS](./apply_css) guide describes how to apply CSS definitions in Panel.
```

---

The Design systems in Panel are set up to be overridden by CSS variables. The usual order of fallbacks for CSS variables is the following:

1. User defined design variables (e.g. `--design-primary-color`)
2. Editor/notebook dependent variables (e.g. `--jp-brand-color0`, for JupyterLab)
3. The theme CSS variable definitions (e.g. `--panel-primary-color`)

To override a particular style we therefore simply have to override one of the user defined design variables:

| Variable                         | Description                                            |
|----------------------------------|--------------------------------------------------------|
| `--design-primary-color`         | Primary color of the design.                           |
| `--design-primary-text-color`    | Color of text rendered on top of primary color.        |
| `--design-secondary-color`       | Secondary color of the design.                         |
| `--design-secondary-text-color`  | Color of text rendered on top of secondary color.      |
| `--design-background-color`      | Color of the background layer.                         |
| `--design-background-text-color` | Color of text rendered on top of the background layer. |
| `--design-surface-color`         | Color of the surface layer.                            |
| `--design-surface-text-color`    | Color of text rendered on top of the surface layer.    |

```{note}
Background and surface colors generally are only set at the template level.
```

When and how to set these variables depends on the precise use case, e.g. if you consistently want to override the colors in a template, use the `Template.config.raw_css` or `Template.config.css_files` parameters to define an inline or imported stylesheet that will apply across the entire template.

For global overrides that apply in all scenarios you can use the `pn.config.global_css` parameter, e.g. here we initialize it via the `pn.extension`:

```{pyodide}
import panel as pn

pn.extension(design='material', global_css=[':root { --design-primary-color: purple; }'])
```

When defining design variable overrides globally use the `:root` CSS selector, which applies the variable from the root on down.

```{pyodide}
pn.Tabs(
    ('Slider', pn.widgets.FloatSlider(start=0, end=7, value=3)),
    ('Button', pn.widgets.Button(name='Click me!', button_type='primary'))
)
```

Alternatively you can also define it directly on a component by adding it to the `stylesheets` and prefixing it with the `:host` selector:

```{pyodide}
pn.Tabs(
    ('Slider', pn.widgets.FloatSlider(
	    start=0, end=7, value=3, stylesheets=[':host { --design-primary-color: red; }']
	)),
    ('Button', pn.widgets.Button(name='Click me!', button_type='primary'))
)
```

## Related Resources
