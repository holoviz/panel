# Apply a Design

In Panel, you can effortlessly style your apps using pre-built *designs*, even if you have no prior frontend development experience. These *designs*, provide ready-made visual themes for your applications:

- **"bootstrap"**: This design is based on the popular [Bootstrap](https://getbootstrap.com/) library, offering a sleek and responsive user interface.
- **"fast"**: Utilizing the [Microsoft Fast Design](https://www.fast.design/) library, this design emphasizes speed and modern aesthetics.
- **"material"**: Inspired by Google's [Material Design](https://m3.material.io/), this design provides a clean and intuitive user experience.
- **"native"**: The default styling inherited from [Bokeh](https://bokeh.org/) ensures compatibility and consistency.

Additionally, Panel supports both `"default"` and `"dark"` themes to further customize the appearance of your application.

:::{note}
When we ask to *run the code* in the sections below, we may execute the code directly in the Panel documentation by using the green *run* button, in a notebook cell, or in a file named `app.py` served with `panel serve app.py --autoreload`.
:::

## Change the Design

Lets give our apps a *clean and intuitive user experience* using the `"material"` *design*.

Run the code:

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

Try changing the `design` from `"material"` to `"bootstrap"`, `"fast"`, or `"native"`.

## Change the Theme

Select a *tab* and continue

::::{tab-set}

:::{tab-item} Python Script
:sync: script

Run the code:

```{pyodide}
import panel as pn

pn.extension(design="fast", theme="dark")

pn.Column(
    pn.widgets.FloatSlider(name="Slider"),
    pn.widgets.TextInput(name="TextInput"),
    pn.widgets.Select(name="Select", options=["Wind Turbine", "Solar Panel", "Battery Storage"]),
    pn.widgets.Button(name="Click me!", icon="hand-click", button_type="primary"),
    styles={"background": "#181818"} # remove this line
).servable()
```

Remove the line `styles={"background": "#181818"} ...`. Its only needed in the Panel docs.

Try changing the `theme` from `"dark"` to `"default"`.

:::

:::{tab-item} Notebook
:sync: script

In the notebook, the `theme` automatically adapts to the current JupyterLab theme.

Try switching the JupyterLab Theme from Dark to Light or vice versa.

It should look like

![Jupyterlab Theme Switching](https://assets.holoviz.org/panel/tutorials/jupyterlab_theme_support.gif)

:::

::::

## Recap

Panel does not require frontend developer experience; instead, we provide high-level `design`s to style our apps:

- `"bootstrap"`: Based on the [Bootstrap](https://getbootstrap.com/) library
- `"fast"`: Based on the [Microsoft Fast Design](https://www.fast.design/) library
- `"material"`: Based on [Material Design](https://m3.material.io/)
- `"native"`: The default styling inherited from [Bokeh](https://bokeh.org/).

We also support the `"default"` and `"dark"` `theme`s.

## References

### How-to

- [Apply a Design](../../how_to/styling/design.md)
- [Customize a Design](../../how_to/styling/design_variables.md)
- [Customize Loading Icon](../../how_to/styling/load_icon.md)
- [Toggle themes](../../how_to/styling/themes.md)

### Explanation

- [Designs and Theming](../../explanation/styling/design.md)
