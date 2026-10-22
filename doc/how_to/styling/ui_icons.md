# Use Icons

This guide shows how to use Material icons in `panel.ui` components, both through the `icon` parameter and inline in text.

---

The `panel.ui` components ship with the [Material Icons](https://fonts.google.com/icons?icon.set=Material+Icons) font. This means you can use any of these icons in components that accept an `icon` and also include them in `Markdown` and `HTML` content.

## `icon` parameter

Many `panel.ui` components, e.g. [`Button`](../../reference/widgets/Button), [`ButtonIcon`](../../reference/widgets/ButtonIcon) and [`Toggle`](../../reference/widgets/Toggle), accept an `icon` parameter. Its value is the *snake_case* ligature name of the icon, which you can look up in the [Material Icons library](https://fonts.google.com/icons?icon.set=Material+Icons).

Icons are filled by default. To use the outlined variant, append `_outlined` to the icon name:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Row(
    pn.ui.ButtonIcon(icon="lightbulb"),
    pn.ui.ButtonIcon(icon="lightbulb_outlined"),
)
```

:::{tip}
The `icon` parameter also accepts an SVG string, e.g. `icon="<svg ...>...</svg>"`, if you need an icon that is not part of the Material library. The SVG is rendered in the current text color.
:::

:::{note}
Only the filled and outlined Material Icons fonts are bundled. The rounded and sharp variants (`_rounded`, `_sharp`) are not available and render as plain text.
:::

## Icons in `Markdown` and `HTML`

You can include icons in `Markdown` and `HTML` content by wrapping the icon name in an element with the `material-icons` or `material-icons-outlined` class:

```{pyodide}
pn.ui.Column(
    'Here is a lightbulb: <span class="material-icons" style="font-size: 2em;">lightbulb</span>',
    'Here is an outlined lightbulb: <span class="material-icons-outlined" style="font-size: 2em;">lightbulb</span>'
)
```

## Icons in text (`:material/...:` tokens)

You can embed icons directly in the text displayed by `panel.ui` components using the `:material/<icon>:` token syntax:

```{pyodide}
pn.ui.Select(
    label="Mode",
    options=[
        "Zoom :material/zoom_out_map:",
        "Explore :material/explore:",
    ],
)
```

You can also pass per-icon options after the icon name as `@key=value` pairs, separated by commas:

```{pyodide}
pn.ui.Button(
    label="Warn :material/zoom_out_map@size=large,color=warning:",
)
```

The supported per-icon options are:

| Option | Description | Example |
| --- | --- | --- |
| `color` | Theme color or CSS color of the icon | `@color=warning` |
| `variant` | Icon variant: `filled` or `outlined` | `@variant=outlined` |
| `size` | Icon size, either `small`, `medium`, `large` or a CSS size | `@size=large` |
| `icon_size` | Explicit CSS font size of the icon | `@icon_size=2rem` |

Options apply only to the token where they appear. Unknown options are ignored, and text that is not a valid token (e.g. `:material/not an icon:`) is left untouched.

### Where tokens are supported

Tokens are rendered wherever a `panel.ui` component displays text:

- Button, `Fab`, toggle, chip, pill, rating and icon labels.
- Input, select, autocomplete, checkbox, radio, switch, slider, picker and color-picker labels, helper text, option labels, group headers and selected values.
- Menu, menu button, split button, menu bar, list, tree, breadcrumb, stepper and speed-dial labels, hints and tooltips.
- `Tabs` tab names, `Card`, `Details` and `Accordion` titles, `Alert` titles, `Dialog` titles and `Page`/app bar titles.
- Widget `description` tooltips, the `Tooltip` wrapper, `Badge` content and notifications.

### Accessibility and string-only slots

Some slots can only hold plain strings, e.g. `aria-label`, native `title` tooltips, `alt` text, input `placeholder` values, the floating label of an outlined input and the options of a native `MultiSelect`. In those slots the token is stripped and the readable text is used instead, so a label of `":material/add: Create"` produces the accessible name `Create`. If the text consists only of tokens, the humanized icon name is used, e.g. `":material/zoom_out_map:"` becomes `zoom out map`.

### Limitations

- Titles supplied as Panel components (e.g. `Card.header`) are rendered as-is; token parsing only applies to string titles and names.
- `Card`, `Details`, `Accordion` and `Tabs` titles continue to support HTML. HTML and tokens can be mixed, e.g. `":material/dashboard: <b>Overview</b>"`.
- Classic Panel and Bokeh components (`pn.widgets`, `pn.Tabs`, the `Markdown` and `HTML` panes, plots, plot tooltips and axis labels) have no token renderer and display the token as literal text. Use the `material-icons` span syntax shown above in `Markdown` and `HTML` panes instead.
