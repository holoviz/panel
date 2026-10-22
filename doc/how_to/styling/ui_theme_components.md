# Theme Components

This guide shows how to customize `panel.ui` components across an entire application by adding a `components` key to the `theme_config`. You can change default props, override styles and style individual variants, which keeps the look and feel of your app consistent. If your customizations grow extensive, consider writing your own component classes instead, since they are easier to maintain.

---

Every `panel.ui` component is built on a [Material UI](https://mui.com/material-ui/) component, and `theme_config` accepts a [Material UI theme](https://mui.com/material-ui/customization/theming/). The `components` key of that theme is keyed by the name of the underlying Material UI component, e.g. `MuiButton` or `MuiCard`.

A `theme_config` applies to the component it is set on and to everything rendered inside it, so setting it on a `pn.ui.Page` or a top-level layout themes the whole app. The examples below set it on individual components to keep them short.

## Theme default props

Every Material UI component has its own default props. You can override these defaults by specifying `defaultProps` under the component's key in `theme_config["components"]`. For example, to disable the ripple effect on a `Button`:

```{pyodide}
import panel as pn

pn.extension()

custom_theme = {
    "components": {
        "MuiButton": {
            "defaultProps": {
                "disableRipple": True
            }
        }
    }
}

pn.ui.Button(label="No Ripple!", theme_config=custom_theme).servable()
```

:::{tip}
The key for each component may vary. For instance, the ripple is implemented by `MuiButtonBase`, which is shared by all buttons, so overriding `MuiButtonBase` disables the ripple on every button-like component at once. You can find the component names and their props in the [Material UI documentation](https://mui.com/material-ui/all-components/), usually in the *API* or *Customization* section of each component page.
:::

## Theme style overrides

Use `styleOverrides` to change the CSS of a component everywhere it is used. Each of the component's "slots" is mapped to a nested dictionary key, and the `root` slot usually targets the component's outermost element.

```{pyodide}
custom_theme = {
    "components": {
        "MuiButton": {
            "styleOverrides": {
                "root": {
                    "fontSize": "1rem"
                }
            }
        }
    }
}

pn.ui.Button(label="Styled Button", theme_config=custom_theme).servable()
```

Multiple nesting levels are possible, e.g. `styleOverrides["root"][".my-class"] = {...}` if you need to target nested elements.

## Variants

Some components have parameters like `variant` or `color` that change their appearance. You can add a `variants` list to `styleOverrides["root"]` to apply styling conditionally, based on the value of these props.

### Overriding styles for an existing variant

For example, to increase the border thickness of a `Card` when `variant="outlined"`:

```{pyodide}
custom_theme = {
    "components": {
        "MuiCard": {
            "styleOverrides": {
                "root": {
                    "variants": [
                        {
                            "props": {"variant": "outlined"},
                            "style": {
                                "borderWidth": "3px"
                            }
                        }
                    ]
                }
            }
        }
    }
}

pn.ui.Card(
    "Card content", title="Thick Outlined Card", variant="outlined", theme_config=custom_theme
).servable()
```

## Theme variables

You can also adjust global theme variables like typography or spacing, which affect how all components render. For example, to increase the font size of all button labels:

```{pyodide}
custom_theme = {
    "typography": {
        "button": {
            "fontSize": "1rem"
        }
    }
}

pn.ui.Button(label="Big Button Text", theme_config=custom_theme).servable()
```

These theme variables can be combined with component overrides in a single `theme_config`. See [Customize Typography](ui_typography) and [Customize the Palette](ui_palette) for more on the global variables.

## Summary

1. **Default props**: Set `defaultProps` to override the default props of any Material UI component.
2. **Style overrides**: Use `styleOverrides["root"]` (and other slots) to change CSS globally.
3. **Variants**: Style components conditionally based on props such as `variant` or `color`.
4. **Theme variables**: Adjust base typography, spacing and more for broad changes across all components.

With these tools you can tailor `panel.ui` components to your brand and user experience, whether you need slight tweaks or a thorough restyling. To see how these pieces fit together in a real application, read [Apply Branding](ui_branding).

## Related Resources

- [Customize Themes & Styles](ui_themes_and_styles)
- [Customize the Palette](ui_palette)
- [Customize Typography](ui_typography)
