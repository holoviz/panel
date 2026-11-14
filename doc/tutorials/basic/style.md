# Enhance the Style

Let's elevate the appearance of our Panel components using the power of [*CSS*](https://www.w3schools.com/css/)!

By employing *CSS*, we can finely adjust the look and feel of our wind turbine data apps, ensuring they are visually appealing and user-friendly. Panel offers three ways to do so:

- `sx` styles a `pn.ui` component, including its inner parts and its hover and dark-mode states.
- `styles` styles the **container** of any component.
- `stylesheets` styles the **contents** of classic components, such as the `Number` indicator.

:::{note}
To execute the code snippets below, feel free to run them directly in the Panel documentation via the convenient green *run* button, within a notebook cell, or within a `app.py` file served with `panel serve app.py --dev`.
:::

## Utilize `sx`

The `sx` parameter accepts a dictionary of CSS properties for a `pn.ui` component. It follows the [Material UI `sx`](https://mui.com/system/getting-started/the-sx-prop/) format, so property names are written in camelCase, like `backgroundColor` instead of `background-color`.

Give it a try:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Button(
    label="Start Turbine",
    icon="play_arrow",
    sx={
        "backgroundColor": "teal",
        "color": "white",
        "borderRadius": "20px",
        "paddingX": 3,
        "&:hover": {"backgroundColor": "darkslategray"},
    },
).servable()
```

Hover over the button to see the `"&:hover"` style kick in. The `&` refers to the component itself, so `"&:hover"` applies while the mouse is over it.

Feel free to experiment by adjusting:

- The `backgroundColor` from `teal` to `goldenrod`.
- The `borderRadius` from `20px` to `0px`.

### Style the Inner Parts

A `pn.ui` component is built from several parts. A slider, for example, consists of a *rail*, a *track* and a *thumb*. You can target these parts with nested selectors that start with `"& "` followed by the CSS class of the part:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.FloatSlider(
    label="Wind Speed (m/s)",
    start=0,
    end=25,
    value=8.6,
    sx={
        "& .MuiSlider-thumb": {"borderRadius": "2px", "backgroundColor": "goldenrod"},
        "& .MuiSlider-track": {"backgroundColor": "teal", "borderColor": "teal"},
        "& .MuiSlider-rail": {"backgroundColor": "lightgray"},
    },
).servable()
```

:::{tip}
To find the CSS class of a part, right-click it in the browser and select *Inspect*. The [Material UI documentation](https://mui.com/material-ui/all-components/) lists the classes of each component too.
:::

### Adapt to the Theme

A style that looks good in the light theme may not look good in the dark theme. In the dark theme, components are wrapped in an element with the `mui-dark` class, so the selector `".mui-dark &"` applies a style only in the dark theme:

```{pyodide}
import panel as pn

pn.extension()

pn.ui.Paper(
    pn.ui.ThemeToggle(),
    pn.ui.Typography("Turbine 42 is running", variant="h6"),
    sx={
        "padding": 2,
        "borderLeft": "6px solid teal",
        ".mui-dark &": {"borderLeft": "6px solid turquoise"},
    },
).servable()
```

Click the toggle to see the border color change along with the theme.

:::{note}
`sx` is the place for one-off styling of a single component. To change the colors or fonts of all components in your app, use `theme_config` as shown in the [Apply a Theme](design.md) tutorial.
:::

## Utilize `styles`

With `styles`, we can effortlessly style the **container** of any component, whether it is a `pn.ui` component, a pane or a classic indicator. Here we use it on the [`Number`](../../reference/indicators/Number.md) indicator.

Give it a try:

```{pyodide}
import panel as pn

pn.extension()

outer_style = {
    'background': '#f9f9f9',
    'border-radius': '5px',
    'border': '2px solid black',
    'padding': '20px',
    'box-shadow': '5px 5px 5px #bcbcbc',
    'margin': "10px",
}

pn.ui.Number(
    label="Wind Speed",
    value=8.6,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
    styles=outer_style,
).servable()
```

Feel free to experiment by adjusting:

- The `border` color from `black` to `teal`.
- The `padding` from `20px` to `50px`.

:::{note}
Unlike `sx`, the keys of `styles` are plain CSS property names, like `border-radius`.
:::

## Employ `stylesheets`

While `styles` beautify the outer container, they don't directly impact the styling of the **contents** within the component. For classic components like the `Number` indicator, `stylesheets` let you reach inside.

Give this a go:

```{pyodide}
import panel as pn

pn.extension()

outer_style = {
    'background': '#f9f9f9',
    'border-radius': '5px',
    'border': '2px solid black',
    'padding': '20px',
    'box-shadow': '5px 5px 5px #bcbcbc',
    'margin': "10px",
}

inner_stylesheet = """
div:nth-child(2) {
  background-color: pink;
  border-radius: 5px;
  padding: 10px;
  margin: 10px;
}
"""

pn.ui.Number(
    label="Wind Speed",
    value=8.6,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
    styles=outer_style,
    stylesheets=[inner_stylesheet]
).servable()
```

Feel free to play with changing the `background-color` from `pink` to `lightgray`.

:::{tip}
The value of the `Number` indicator is displayed with a `font_size` of `54pt` by default. Set `font_size="32pt"` if you'd like it smaller.
:::

:::{warning}
`stylesheets` don't apply to Material components like `pn.ui.Button` or `pn.ui.FloatSlider`. Use `sx` to style those.
:::

:::{tip}
For more insights into `stylesheets`, refer to the [Apply CSS](../../how_to/styling/apply_css.md) how-to guide.
:::

## Wrapping Up

With *CSS*, we can refine the style of our Panel components, ensuring they're visually appealing and provide a delightful user experience:

- Use `sx` to style `pn.ui` components, including hover states, inner parts and the dark theme.
- Use `styles` to style the container of any component.
- Use `stylesheets` to style the contents of classic components.

## Resources

### Tutorials

- [Apply a Theme](design.md)

### How-to

- [Apply CSS](../../how_to/styling/apply_css.md)
- [Style Altair Plots](../../how_to/styling/altair.md)
- [Style Echarts Plots](../../how_to/styling/echarts.md)
- [Style Matplotlib Plots](../../how_to/styling/matplotlib.md)
- [Style Plotly Plots](../../how_to/styling/plotly.md)
- [Style Vega/ Altair Plots](../../how_to/styling/vega.md)
