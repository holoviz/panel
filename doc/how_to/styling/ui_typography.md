# Customize Typography

The `pn.ui` components share a typography system inspired by Material UI. Fonts and sizes can be customized globally with a `theme_config`, or overridden at the component level with `sx`.

---

## Font family

To change the default font family across your entire app, specify it in `theme_config["typography"]["fontFamily"]`. The theme typography applies to components that render a typography variant, so make sure to set a `variant` on `Typography` components:

```{pyodide}
import panel as pn

pn.extension()

my_theme = {
    "typography": {
        "fontFamily": (
            "-apple-system, "
            "BlinkMacSystemFont, "
            "\"Segoe UI\", "
            "Roboto, "
            "\"Helvetica Neue\", "
            "Arial, sans-serif, "
            "\"Apple Color Emoji\", "
            "\"Segoe UI Emoji\", "
            "\"Segoe UI Symbol\""
        )
    }
}

pn.ui.Typography(
    "Hello with a System Font!",
    variant="body1",
    theme_config=my_theme
).servable()
```

## Font size

Like Material UI, the `pn.ui` components use `rem` units for font sizes. By default browsers render `1rem = 16px`, but users may override this in their browser settings. This improves accessibility, allowing your UI to scale gracefully if the user increases the default font size.

To change the base font size, set `theme_config["typography"]["fontSize"]` (in pixels, the default is 14). All variants are scaled relative to it:

```{pyodide}
my_theme = {
    "typography": {
        "fontSize": 12
    }
}

pn.ui.Typography(
    "Smaller base font size.",
    variant="body1",
    theme_config=my_theme
).servable()
```

### Responsive font sizes

To make font sizes responsive, use media queries in the `sx` parameter of individual components. For a single [`Typography`](../../reference/panes/Typography) component:

```{pyodide}
pn.ui.Typography(
    "Responsive Typography",
    sx={
        "fontSize": "1.2rem",
        "@media (min-width: 600px)": {
            "fontSize": "1.5rem"
        },
        "@media (min-width: 900px)": {
            "fontSize": "2.4rem"
        }
    }
).servable()
```

To systematically apply responsive font sizes across all headings or body text, define them in `theme_config["typography"]["h1"]`, `"h2"`, etc. using nested media queries.

### HTML font size

Some developers prefer to set the `<html>` font size to 10px (or 62.5%) for simpler `rem` arithmetic. In that case:

1. Adjust your global HTML styles (e.g. via `pn.config.raw_css` or a custom stylesheet, see [Apply CSS](apply_css)) to `html { font-size: 62.5%; }`, which makes `1rem = 10px`.
2. Let the components know the new root size by setting `theme_config["typography"]["htmlFontSize"] = 10`.

:::{note}
Be mindful that changing the base font size can affect accessibility if a user depends on the default 16px.
:::

## Variants

There are 13 default text variants:

- `h1`, `h2`, `h3`, `h4`, `h5`, `h6`
- `subtitle1`, `subtitle2`
- `body1`, `body2`
- `button`
- `caption`
- `overline`

Each variant can be styled independently via `theme_config["typography"][<variant>]`:

```{pyodide}
my_theme = {
    "typography": {
        "subtitle1": {"fontSize": 12},
        "body1": {"fontWeight": 500},
        "button": {"fontStyle": "italic"},
    }
}

pn.ui.Column(
    pn.ui.Typography("I'm a subtitle", variant="subtitle1"),
    pn.ui.Typography("I'm body text", variant="body1"),
    pn.ui.Button(label="Italic button"),
    theme_config=my_theme,
).servable()
```

Any component that uses these variants, including the text of widgets like [`Button`](../../reference/widgets/Button), picks up your custom definitions.

### Adding new variants

You can also create entirely new variants (e.g. `poster`) by adding them to the typography dictionary and referencing them by name:

```{pyodide}
my_theme = {
    "typography": {
        "poster": {
            "fontSize": "4rem",
            "color": "red"
        },
    }
}

pn.ui.Typography(
    "I'm a poster", theme_config=my_theme, variant="poster"
).servable()
```

## Summary

- **Set the global font family** in `theme_config["typography"]["fontFamily"]`.
- **Change the base font size** with `theme_config["typography"]["fontSize"]` (default 14px).
- **Use `rem` for accessibility**, which respects the user's global font scaling.
- **Override variants individually** (`h1`, `body2`, `button`, etc.) in the typography section of `theme_config`.
- **Add variants** for custom text styles (e.g. a giant `poster` style).
- **Use media queries** in `theme_config` or the `sx` parameter for responsive scaling.
- **Change the HTML root size** via CSS and `htmlFontSize` to simplify `rem` arithmetic, but keep user accessibility in mind.

See [Customize Themes and Styles](ui_themes_and_styles) for an overview of the other styling options.
