# Customize Themes and Styles

The `pn.ui` components share the consistent design language of [Material UI](https://mui.com/material-ui/), which makes them easy to customize. Styling is applied with the `sx` parameter, while theming is achieved through the inheritable `theme_config` parameter. This guide walks through both approaches with a series of examples.

This guide was adapted from the Material UI [How to customize](https://mui.com/material-ui/customization/how-to-customize/) guide.

---

## Styling layers overview

Panel provides multiple tools for styling, each suited to different needs:

| Tool | Purpose | Scope |
|---|---|---|
| `sx` | Style component internals (one-off tweaks, experiments) | Local to one instance |
| `theme_config` | Define app-wide palette, typography and defaults | Global (flows to all children) |
| `styles` | Style the outer container box (spacing, borders, backgrounds) | Local to one instance |
| `stylesheets` | Style component internals via CSS selectors | Local to one instance |

A useful mental model: start with `sx` for local customizations, use `theme_config` for consistency, use `styles` to style the container around a component, and reach for `stylesheets` only when styling classic Panel components (see [Apply CSS](apply_css)).

## One-off customizations with `sx`

To change the styles of a single component instance, use the `sx` parameter. This is ideal for quick, local customizations like tweaking padding, changing colors or adding hover effects.

### The `sx` parameter

All `pn.ui` components accept an `sx` parameter that lets you pass in style overrides:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Button(
    label="Click Me!",
    sx={
        "color": "white",
        "backgroundColor": "black",
        "&:hover": {
            "backgroundColor": "gray",
        }
    }
).servable()
```

#### Dark and light mode selectors

If you need to apply styling only in dark or light mode, use the `.mui-dark` or `.mui-light` class. The class is set on a container wrapping the component, so the selector has to target an ancestor of the component using `".mui-dark &"`:

```{pyodide}
pn.ui.Row(
    pn.ui.Button(
        label="Click Me!",
        sx={
            "color": "white",
            "backgroundColor": "black",
            "&:hover": {
                "backgroundColor": "pink",
            },
            ".mui-dark &:hover": {
                "backgroundColor": "orange",
            }
        }
    ),
    pn.ui.ThemeToggle(),
).preview()
```

#### Targeting nested component parts

Sometimes you need to style a nested part of a component, for instance the thumb of a slider or the label of a checkbox. Use the `&` selector to target nested Material UI class names:

```{pyodide}
pn.ui.FloatSlider(
    sx={
        "& .MuiSlider-thumb": {
            "borderRadius": 0  # square instead of round
        }
    }
).servable()
```

You can also combine nested selectors with dark and light mode:

```{pyodide}
pn.ui.Row(
    pn.ui.FloatSlider(
        sx={
            "& .MuiSlider-thumb": {
                "borderRadius": 0,
                "backgroundColor": "black",
            },
            ".mui-dark & .MuiSlider-thumb": {
                "backgroundColor": "white",
            }
        }
    ),
    pn.ui.ThemeToggle(),
).preview()
```

:::{note}
Even though the `pn.ui` components reuse Material UI's internal class names, these names are subject to change. Keep an eye on the release notes if you override nested classes.
:::

Learn more about the [`sx` prop in the Material UI docs](https://mui.com/system/getting-started/the-sx-prop/).

## Global theming with `theme_config`

For app-wide consistency, use `theme_config` to define defaults (colors, typography, shape) that flow down to all child components. This is the most maintainable approach for larger apps.

### Basic theme configuration

Define a theme on a component and it applies to that component and all of its children:

```{pyodide}
theme_config = {
    "palette": {
        "primary": {"main": "#d219c9"},
        "secondary": {"main": "#dc004e"},
    }
}

pn.ui.Button(
    label="Themed Button", theme_config=theme_config, color="primary"
).servable()
```

:::{important}
Palette colors must be specified as hex, `rgb()`, `rgba()`, `hsl()` or `hsla()` strings. Named CSS colors such as `"teal"` are not supported by Material UI's color manipulation functions and will raise an error.
:::

### Mode-specific themes

Provide distinct theme configs for dark and light mode using `"light"` and `"dark"` keys:

```{pyodide}
theme_config = {
    "light": {
        "palette": {
            "primary": {"main": "#d219c9"},
            "secondary": {"main": "#dc004e"},
        }
    },
    "dark": {
        "palette": {
            "primary": {"main": "#dc004e"},
            "secondary": {"main": "#d219c9"},
        }
    }
}

pn.ui.Row(
    pn.ui.Button(
        label="Global Button", theme_config=theme_config, color="primary"
    ),
    pn.ui.ThemeToggle(),
).preview()
```

### Theme inheritance

The most powerful feature of `theme_config` is that child components automatically inherit the theme of their parent. This lets you style your entire app from one top-level configuration:

```{pyodide}
pn.ui.Card(
    pn.ui.Button(label="Child Button", color="primary"),  # Inherits the Card's theme
    title="Parent Card",
    theme_config={
        "palette": {
            "primary": {"main": "#d219c9"},
        }
    }
).servable()
```

Here the child `Button` automatically inherits the primary color of its parent. We recommend setting the theme on your top-level container (e.g. `Page`, `Container` or `Row`) so it cascades throughout your app.

### Comparison: `sx` vs `theme_config`

Both approaches can achieve the same visual result but serve different purposes.

Using `sx` (local):

```{pyodide}
pn.ui.Button(
    label="Local Style",
    sx={"backgroundColor": "#d219c9", "color": "white"}
).servable()
```

Using `theme_config` (global):

```{pyodide}
theme = {
    "palette": {
        "primary": {"main": "#d219c9"},
    }
}

pn.ui.Row(
    pn.ui.Button(label="Global Style", color="primary"),
    theme_config=theme,
).servable()
```

Use `sx` for one-off exceptions or quick experiments and `theme_config` when you want consistency across many components or the entire app. The two combine well: set global defaults with `theme_config`, then use `sx` for local overrides.

## Container styling with `styles`

The `styles` parameter styles the outer container of any Panel component. It is well suited for spacing, borders, backgrounds and shadows around the component itself (not its internals).

```{pyodide}
container_style = {
    "background": "#f8fafc",
    "border": "1px solid #dce3eb",
    "border-radius": "10px",
    "padding": "12px",
    "box-shadow": "0 2px 8px rgba(0,0,0,0.08)",
}

pn.ui.Row(
    pn.ui.Button(label="Button in styled container", color="primary", styles=container_style),
).servable()
```

### Difference between `sx` and `styles`

`sx` styles the component internals (the text and background of a `Button`, the handle of a `Slider`, etc.), while `styles` styles the outer container box that wraps around the component. The example below uses both:

```{pyodide}
# styles: changes the wrapper box around the button
container_style = {
    "background": "#e3f2fd",
    "border": "2px solid #1976d2",
    "border-radius": "8px",
    "padding": "16px",
}

# sx: changes the button itself
button_sx = {
    "backgroundColor": "#ff6b6b",
    "color": "white",
    "&:hover": {"backgroundColor": "#ff5252"}
}

pn.ui.Row(
    pn.ui.Button(
        label="Styled Button",
        sx=button_sx,
        styles=container_style
    ),
).servable()
```

## Putting it all together

A real app typically combines multiple approaches:

```{pyodide}
app_theme = {
    "light": {
        "palette": {
            "primary": {"main": "#6a1b9a"},
            "secondary": {"main": "#1565c0"},
        },
        "shape": {"borderRadius": 12},
    },
    "dark": {
        "palette": {
            "primary": {"main": "#9575cd"},
            "secondary": {"main": "#64b5f6"},
        },
        "shape": {"borderRadius": 12},
    },
}

card_container = {
    "padding": "8px",
    "background": "rgba(0,0,0,0.02)",
}

button_sx = {
    "fontWeight": 700,
    "&:hover": {"transform": "scale(1.02)"}
}

pn.ui.Row(
    pn.ui.Card(
        pn.ui.Button(
            label="Submit",
            color="primary",
            sx=button_sx,  # Local exception
        ),
        title="Form",
        styles=card_container,  # Container styling
    ),
    pn.ui.ThemeToggle(),
    theme_config=app_theme,  # Global theme
).preview(height=300)
```

## Related guides

- [Customize the Color Palette](ui_palette)
- [Customize Typography](ui_typography)
- [Control Dark Mode](ui_dark_mode)
- [Pick Colors](ui_pick_colors)
