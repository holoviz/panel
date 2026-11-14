# Apply a Theme

Panel empowers you to effortlessly theme your apps, regardless of your prior experience in frontend development. The `pn.ui` components are built on Google's [Material Design](https://m3.material.io/) and share a single theme, which lets you:

- Switch between a light and a dark *theme*.
- Brand your app with your own colors and fonts using `theme_config`.
- Pick a `color` and `variant` for individual components.

:::{note}
In the sections below, you can run the provided code directly in the Panel documentation by utilizing the green *run* button, executing it in a notebook cell, or saving it in a file named `app.py` and serving it with `panel serve app.py --dev`.
:::

## Toggle the Theme

Every `pn.ui` component comes in a light and a dark version. The [`ThemeToggle`](../../reference/templates/ThemeToggle.md) lets your users switch between them.

Run the following code and click the toggle:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Paper(
    pn.ui.ThemeToggle(),
    pn.ui.FloatSlider(label="Wind Speed (m/s)", start=0, end=25, value=8.6),
    pn.ui.TextInput(label="Site Name"),
    pn.ui.Select(label="Asset", options=["Wind Turbine", "Solar Panel", "Battery Storage"]),
    pn.ui.Button(label="Click me!", icon="touch_app", color="primary"),
    elevation=2,
).servable()
```

The toggle switches the theme of all components on the page at once.

:::{tip}
A [`Page`](../../reference/templates/Page.md) has a theme toggle built in, so you only need to add a `ThemeToggle` yourself when you're not using a `Page`.
:::

Choose a *tab* to learn how to pick the theme your app starts in:

::::{tab-set}

:::{tab-item} Python Script
:sync: script

Pass `theme="dark"` to the `Page` to start the app in the dark theme. Copy the code below into `app.py` and serve it with `panel serve app.py --dev`:

```python
import panel as pn

pn.extension()

pn.ui.Page(
    title="Wind Turbine Monitor",
    sidebar=[
        pn.ui.FloatSlider(label="Wind Speed (m/s)", start=0, end=25, value=8.6),
        pn.ui.Select(label="Asset", options=["Wind Turbine", "Solar Panel", "Battery Storage"]),
    ],
    main=["# All turbines are running"],
    theme="dark",
).servable()
```

Users can still switch to the light theme with the toggle in the header. Set `theme_toggle=False` to keep the app dark, for example on a wall screen in a control room.

:::

:::{tab-item} Notebook
:sync: script

In the notebook, the `theme` automatically adapts to the current JupyterLab theme.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Column(
    pn.ui.FloatSlider(label="Wind Speed (m/s)", start=0, end=25, value=8.6),
    pn.ui.TextInput(label="Site Name"),
    pn.ui.Select(label="Asset", options=["Wind Turbine", "Solar Panel", "Battery Storage"]),
    pn.ui.Button(label="Click me!", icon="touch_app", color="primary"),
).servable()
```

Experiment by switching the JupyterLab Theme from Dark to Light or vice versa.

The experience should look something like this:

![Jupyterlab Theme Switching](https://assets.holoviz.org/panel/tutorials/jupyterlab_theme_support.gif)

:::

::::

## Choose Colors and Variants

Many `pn.ui` components accept a `color`, such as `"primary"`, `"secondary"`, `"success"`, `"warning"` or `"error"`, and a `variant` that changes how they are drawn.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Column(
    pn.ui.Row(
        pn.ui.Button(label="Start", icon="play_arrow", color="success"),
        pn.ui.Button(label="Pause", icon="pause", color="warning", variant="outlined"),
        pn.ui.Button(label="Stop", icon="stop", color="error", variant="text"),
    ),
    pn.ui.FloatSlider(label="Blade Pitch (°)", start=0, end=90, value=12, color="secondary"),
    pn.ui.TextInput(label="Site Name", variant="filled"),
).servable()
```

Feel free to experiment by changing the `color` and `variant` of the components.

:::{note}
`color` and `variant` don't exist on every component, and the allowed values differ between components. A `Button` can be `"contained"`, `"outlined"` or `"text"`, while a `TextInput` can be `"outlined"`, `"filled"` or `"standard"`. Check the [Component Gallery](../../reference/index.md) when in doubt.
:::

The `icon` takes the name of any icon from [Material Icons](https://fonts.google.com/icons?icon.set=Material+Icons), such as `"play_arrow"` or `"touch_app"`.

## Brand Your App with `theme_config`

The colors behind `"primary"` and `"secondary"`, the fonts and the roundness of corners all come from the *theme*. With `theme_config` you can change them in one place, and every component inside picks them up.

Run the code below:

```{pyodide}
import panel as pn

pn.extension()

theme_config = {
    "palette": {
        "primary": {"main": "#008080"},
        "secondary": {"main": "#DAA520"},
    },
    "typography": {
        "fontFamily": "Georgia, serif",
    },
    "shape": {"borderRadius": 12},
}

pn.ui.Paper(
    pn.ui.Typography("Turbine Control", variant="h5"),
    pn.ui.FloatSlider(label="Wind Speed (m/s)", start=0, end=25, value=8.6),
    pn.ui.FloatSlider(label="Blade Pitch (°)", start=0, end=90, value=12, color="secondary"),
    pn.ui.Row(
        pn.ui.Button(label="Start", icon="play_arrow", color="primary"),
        pn.ui.Button(label="Calibrate", icon="tune", color="secondary", variant="outlined"),
    ),
    theme_config=theme_config,
    elevation=2,
).servable()
```

Feel free to experiment by changing:

- The `primary` color from `"#008080"` to `"#1565C0"`.
- The `fontFamily` from `"Georgia, serif"` to `"system-ui, sans-serif"`.
- The `borderRadius` from `12` to `0`.

:::{note}
In the code:

- `palette` sets the colors. You only need to provide the `main` color, the lighter and darker shades are computed for you. Specify colors as hex codes, CSS color names such as `"teal"` are not supported.
- `typography` sets the font family, and can also set the size of the base font and of each text variant like `"h5"`.
- `shape` sets the corner radius of buttons, inputs and papers.

The `theme_config` follows the [Material UI theme](https://mui.com/material-ui/customization/theming/) format.
:::

In an app, you'll usually set the `theme_config` on the `Page`, which applies it to the header and to all the components on the page:

```python
import panel as pn

pn.extension()

theme_config = {
    "palette": {
        "primary": {"main": "#008080"},
        "secondary": {"main": "#DAA520"},
    },
}

pn.ui.Page(
    title="Wind Turbine Monitor",
    sidebar=[
        pn.ui.FloatSlider(label="Wind Speed (m/s)", start=0, end=25, value=8.6),
        pn.ui.Button(label="Calibrate", icon="tune", color="secondary"),
    ],
    main=["# All turbines are running"],
    theme_config=theme_config,
).servable()
```

### Different Colors for Light and Dark

A color that works well on a white background may be too dark on a black one. Provide a separate `"light"` and `"dark"` configuration to adapt the colors to the theme:

```{pyodide}
import panel as pn

pn.extension()

theme_config = {
    "light": {"palette": {"primary": {"main": "#00695C"}}},
    "dark": {"palette": {"primary": {"main": "#80CBC4"}}},
}

pn.ui.Paper(
    pn.ui.ThemeToggle(),
    pn.ui.FloatSlider(label="Wind Speed (m/s)", start=0, end=25, value=8.6),
    pn.ui.Button(label="Start", icon="play_arrow", color="primary"),
    theme_config=theme_config,
    elevation=2,
).servable()
```

Click the toggle to see the primary color change along with the theme.

## Recap

You don't need to be a frontend developer to theme your Panel apps:

- `pn.ui` components support a light and a dark theme. A `Page` comes with a theme toggle, and `theme="dark"` starts an app in the dark theme.
- In the notebook, the theme follows the JupyterLab theme.
- `color` and `variant` change the look of individual components.
- `theme_config` sets the palette, typography and shape for every component inside, and can differ between the light and dark theme.

## References

### Component Gallery

- [Page](../../reference/templates/Page.md)
- [ThemeToggle](../../reference/templates/ThemeToggle.md)

### How-to

- [Customize Loading Icon](../../how_to/styling/load_icon.md)
- [Toggle themes](../../how_to/styling/themes.md)

### Explanation

- [Designs and Theming](../../explanation/styling/design.md)
