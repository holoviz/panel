# Enhance the Style

Let's elevate the appearance of our Panel components using the power of [*CSS*](https://www.w3schools.com/css/)!

By employing *CSS*, we can finely adjust the look and feel of our wind turbine data apps, ensuring they are not only visually appealing but also user-friendly.

:::{note}
To execute the code snippets below, feel free to run them directly in the Panel documentation via the convenient green *run* button, within a notebook cell, or within a `app.py` file served with `panel serve app.py --autoreload`.
:::

## Utilize `styles`

With `styles`, we can effortlessly style the **container** of a component.

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

pn.indicators.Number(
    name="Wind Speed",
    value=8.6,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
    styles=outer_style,
).servable()
```

Feel free to experiment by adjusting:

- The `border` color from `black` to `teal`.
- The `padding` from `20px` to `50px`.

## Employ `stylesheets`

While `styles` beautify the outer container, they don't directly impact the styling of the **contents** within the component. Here enters `stylesheets`.

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

pn.indicators.Number(
    name="Wind Speed",
    value=8.6,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
    styles=outer_style,
    stylesheets=[inner_stylesheet]
).servable()
```

Feel free to play with changing the `background-color` from `pink` to `lightgray`.

:::{tip}
For more insights into `stylesheets`, refer to the [Apply CSS](../../how_to/styling/apply_css.md) how-to guide.
:::

## Wrapping Up

With *CSS*, we can refine the style of our Panel components, ensuring they're not only visually appealing but also provide a delightful user experience.

## Resources

### How-to

- [Apply CSS](../../how_to/styling/apply_css.md)
- [Style Altair Plots](../../how_to/styling/altair.md)
- [Style Echarts Plots](../../how_to/styling/echarts.md)
- [Style Matplotlib Plots](../../how_to/styling/matplotlib.md)
- [Style Plotly Plots](../../how_to/styling/plotly.md)
- [Style Vega/ Altair Plots](../../how_to/styling/vega.md)
