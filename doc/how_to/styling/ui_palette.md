# Customize the Color Palette

The palette system of the `pn.ui` components lets you customize component colors to suit your brand. Colors are grouped into default categories (primary, secondary, error, warning, info, success) or custom categories that you define yourself.

---

## Color tokens

Each palette color typically has up to four tokens:

- **main**: The primary shade of the color
- **light**: A lighter variant of main
- **dark**: A darker variant of main
- **contrastText**: A color intended to contrast well against main (usually text)

For example, the default primary color might look like:

```python
primary = {
    'main': '#1976d2',
    'light': '#42a5f5',
    'dark': '#1565c0',
    'contrastText': '#fff',
}
```

To learn more about the theory behind these tokens, check out the [Material Design color system](https://m2.material.io/design/color/).

## Default colors

The `pn.ui` components provide nine default palette categories you can customize:

- default
- primary
- secondary
- error
- warning
- info
- success
- dark
- light

Each has the same four tokens (main, light, dark, contrastText) and corresponds to a value of the `color` parameter of components like [`Button`](../../reference/widgets/Button). These defaults are enough for most apps, but you can add custom palette entries as needed.

## Customizing the default palette

You can override the defaults via the `theme_config` parameter of any `pn.ui` component:

```{pyodide}
import panel as pn

pn.extension()

my_theme = {
    "palette": {
        "primary": {
            "main": "#ff69b4",  # Changed to pink
            "light": "#42a5f5",
            "dark": "#1565c0",
            "contrastText": "#fff",
        },
        "secondary": {
            "main": "#f44336",
        },
    }
}

pn.ui.Button(label="Custom Themed Button", theme_config=my_theme, color='primary')
```

:::{important}
Palette colors must be specified as hex, `rgb()`, `rgba()`, `hsl()` or `hsla()` strings. Named CSS colors such as `"teal"` are not supported by Material UI's color manipulation functions and will raise an error.
:::

### Providing colors directly

For each palette entry (e.g. primary) you can specify `main` (required), and optionally `light`, `dark` and `contrastText`:

```{pyodide}
my_theme = {
    "palette": {
        "primary": {
            "main": "#ff69b4",  # Changed to pink
            # light, dark and contrastText are computed automatically
        },
        "secondary": {
            "main": "#E0C2FF",
            "light": "#F5EBFF",   # optional
            "dark": "#BA99D5",    # optional
            "contrastText": "#47008F",  # optional
        }
    }
}

pn.ui.Row(
    pn.ui.Button(label="Primary", theme_config=my_theme, color='primary'),
    pn.ui.Button(label="Secondary", theme_config=my_theme, color='secondary'),
)
```

### Contrast threshold

When `contrastText` is computed automatically for a color (because you did not specify it), Material UI uses the `contrastThreshold` value. By default it is 3 (a 3:1 contrast ratio), but you can increase it for improved accessibility:

```python
my_theme = {
    "palette": {
        "primary": {
            "main": "#3f50b5",
        },
        "contrastThreshold": 4.5  # Increase for higher contrast
    }
}
```

This helps ensure a better contrast ratio for text displayed over the `primary.main` color.

### Tonal offset

Similarly, the `light` and `dark` tokens are calculated by shifting the luminance of `main`. The `tonalOffset` defaults to 0.2, but you can override it at the top level of your palette:

```python
my_theme = {
    "palette": {
        "tonalOffset": 0.25,
        "primary": {
            "main": "#FF5733",
        },
    }
}
```

This means `light` becomes lighter and `dark` becomes darker relative to `main`.

### Accessibility

For color contrast, the recommendation is a minimum ratio of 4.5:1 for body text (per [WCAG 2.1 Rule 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)). If you rely on the automatically computed `contrastText`, increase `contrastThreshold` to 4.5:

```python
my_theme = {
    "palette": {
        "contrastThreshold": 4.5,
        "primary": {"main": "#3f50b5"},
    }
}
```

You should still verify that the chosen foreground and background colors yield the contrast you want, especially if you are targeting stricter guidelines.

## Dark mode

To use a separate palette in dark mode, nest the palette under `"light"` and `"dark"` keys in the `theme_config`. To enable dark mode, set `dark_theme=True` on individual components or on the [`Page`](../../reference/templates/Page). For more guidance on setting up and toggling dark mode see [Control Dark Mode](ui_dark_mode).

## Summary

- **Default palette**: `default`, `primary`, `secondary`, `error`, `warning`, `info`, `success`, `light`, `dark`
- **Color format**: hex, `rgb()` or `hsl()` strings, not CSS color names
- **Tokens**: `main`, `light`, `dark`, `contrastText`
- **Automatic computations**: If you only specify `main`, the `light`, `dark` and `contrastText` tokens are inferred using `contrastThreshold` and `tonalOffset`.
- **Accessibility**: Increase `contrastThreshold` if you need a higher text contrast ratio.
- **Dark mode**: Supply a mode-specific `theme_config` with `"light"` and `"dark"` keys.

With `theme_config` you can define or override any palette color you need, on a single component or globally across your entire application. See [Pick Colors](ui_pick_colors) for tools that help you choose a palette and [Customize Themes and Styles](ui_themes_and_styles) for an overview of the other styling options.
