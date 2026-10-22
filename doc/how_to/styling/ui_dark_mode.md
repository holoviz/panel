# Control Dark Mode

The `pn.ui` components automatically integrate with Panel's theme configuration. You can force dark mode by setting `dark_theme=True` at the component level or globally via `pn.extension(theme='dark')`.

---

## Dark mode only

If you want a component to always use dark mode, set `dark_theme=True`:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Button(
    label="Dark Button", dark_theme=True
).servable()
```

or set it globally for the whole app:

```python
pn.extension(theme='dark')
```

The theme can also be selected per session by adding `?theme=dark` to the URL of a served app (see [Toggling themes](themes)).

## Managed theme

Rather than setting `dark_theme` on individual components, you will usually want to manage the theme for the whole app and let users switch it. You have two options:

1. Use the [`Page`](../../reference/templates/Page) component, which includes a theme toggle in its header and manages the theme for you. Its `dark_theme` parameter (which can also be passed as `theme="dark"`) sets the initial theme:

```{pyodide}
pn.ui.Page(
    dark_theme=True,
    main=[
        pn.ui.Button(label="Dark Button")
    ],
    title="Dark Mode Demo",
).preview()
```

2. Embed the [`ThemeToggle`](../../reference/templates/ThemeToggle) component, which manages the theme globally and lets the user switch between light and dark mode:

```{pyodide}
pn.ui.Row(pn.ui.Button(label="Hello"), pn.ui.ThemeToggle()).preview()
```

## Notebook themes

When rendered in a VS Code, JupyterLab or nteract notebook, components follow the editor theme automatically. They pick up the theme when they are first rendered and switch along with it whenever you change the theme in the editor, which takes precedence over `dark_theme` and `pn.extension(theme=...)`. Once rendered, a `ThemeToggle` or the `Page` theme toggle can still switch the theme manually until the editor theme changes again.

## Overriding the dark palette

When `dark_theme=True`, components automatically switch to a dark palette. To customize that palette further, for instance to change the primary color, provide a `theme_config` with separate `"dark"` and `"light"` entries, just like you would for other color overrides:

```{pyodide}
theme_config = {
    "dark": {
        "palette": {
            "primary": {
                "main": "#450c0c"
            }
        }
    },
    "light": {
        "palette": {
            "primary": {
                "main": "#eb5252"
            }
        }
    }
}

pn.ui.Button(
    label="Custom Dark",
    dark_theme=True,
    color="primary",
    theme_config=theme_config
).servable()
```

To apply styles only in one mode with the `sx` parameter, use the `.mui-dark` and `.mui-light` selectors described in [Customize Themes and Styles](ui_themes_and_styles). See [Customize the Color Palette](ui_palette) for more on palette configuration.
