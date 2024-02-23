# Apply a Design

Panel empowers you to effortlessly style your apps using pre-built *designs*, regardless of your prior experience in frontend development. These *designs* offer ready-made visual themes for your applications:

- **"bootstrap"**: Embraces the elegance and responsiveness of the [Bootstrap](https://getbootstrap.com/) library.
- **"fast"**: Harnesses the speed and modern aesthetics of the [Microsoft Fast Design](https://www.fast.design/) library.
- **"material"**: Draws inspiration from Google's [Material Design](https://m3.material.io/), providing a clean and intuitive user experience.
- **"native"**: Ensures compatibility and consistency with the default styling inherited from [Bokeh](https://bokeh.org/).

Additionally, Panel supports both `"default"` and `"dark"` themes to further tailor the appearance of your application.

:::{note}
In the sections below, you can run the provided code directly in the Panel documentation by utilizing the green *run* button, executing it in a notebook cell, or saving it in a file named `app.py` and serving it with `panel serve app.py --autoreload`.
:::

## Change the Design

Let's elevate our apps with a *clean and intuitive user experience* by applying the `"material"` *design*.

Run the following code:

```{pyodide}
import panel as pn

pn.extension(design="material")

pn.Column(
    pn.widgets.FloatSlider(name="Slider"),
    pn.widgets.TextInput(name="TextInput"),
    pn.widgets.Select(name="Select", options=["Wind Turbine", "Solar Panel", "Battery Storage"]),
    pn.widgets.Button(name="Click me!", icon="hand-click", button_type="primary"),
).servable()
```

Feel free to experiment by changing the `design` to `"bootstrap"`, `"fast"`, or `"native"`.

## Change the Theme

Choose a *tab* to proceed:

::::{tab-set}

:::{tab-item} Python Script
:sync: script

Run the code below:

```{pyodide}
import panel as pn

pn.extension(design="fast", theme="dark")

pn.Column(
    pn.widgets.FloatSlider(name="Slider"),
    pn.widgets.TextInput(name="TextInput"),
    pn.widgets.Select(name="Select", options=["Wind Turbine", "Solar Panel", "Battery Storage"]),
    pn.widgets.Button(name="Click me!", icon="hand-click", button_type="primary"),
    styles={"background": "#181818"} # styles only necessary in the Panel docs
).servable()
```

Try toggling the `theme` from `"dark"` to `"default"`.

:::

:::{tab-item} Notebook
:sync: script

In the notebook, the `theme` automatically adapts to the current JupyterLab theme.

Experiment by switching the JupyterLab Theme from Dark to Light or vice versa.

The experience should look something like this:

![Jupyterlab Theme Switching](https://assets.holoviz.org/panel/tutorials/jupyterlab_theme_support.gif)

:::

::::

## Recap

You don't need to be a frontend developer to style your Panel apps. With high-level `design`s, you can effortlessly tailor your applications:

- `"bootstrap"`: Based on the [Bootstrap](https://getbootstrap.com/) library.
- `"fast"`: Based on the [Microsoft Fast Design](https://www.fast.design/) library.
- `"material"`: Based on [Material Design](https://m3.material.io/).
- `"native"`: The default styling inherited from [Bokeh](https://bokeh.org/).

Panel also supports the `"default"` and `"dark"` `theme`s.

## References

### How-to

- [Apply a Design](../../how_to/styling/design.md)
- [Customize a Design](../../how_to/styling/design_variables.md)
- [Customize Loading Icon](../../how_to/styling/load_icon.md)
- [Toggle themes](../../how_to/styling/themes.md)

### Explanation

- [Designs and Theming](../../explanation/styling/design.md)
