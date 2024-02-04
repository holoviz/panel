# Use Styles

We can finetune the style of our Panel components with [*css*](https://www.w3schools.com/css/):

- Use `styles` to style the *outer container*.
- Use `stylesheets` to style the *inner contents of the container*.

This will ensure our wind turbine data apps are both aesthetically pleasing and user-friendly.

:::{note}
When we ask to *run the code* in the sections below, we may execute the code directly in the Panel docs via the green *run* button, in a cell in a notebook, or in a file `app.py` that is served with `panel serve app.py --autoreload`.
:::

## Use `styles`

Applying `styles` allows us to style the **container** of a component in a straightforward manner.

Run the code below:

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

indicator = pn.indicators.Number(
    name="Wind Speed",
    value=8.6,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
    styles=outer_style,
).servable()
```

Try changing the

- `border` color from `black` to `teal`.
- `padding` from `20px` to `50px`.

## Use `stylesheets`

Since `styles` only applies to the outer `<div>` that holds the component, we cannot use `styles` to directly modify the styling of the **contents** of the component. This is where `stylesheets` come in.

Run the code below:

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

indicator = pn.indicators.Number(
    name="Wind Speed",
    value=8.6,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
    styles=outer_style,
    stylesheets=[inner_stylesheet]
).servable()
```

Try changing the `background-color` from `pink` to `lightgray`.

:::{note}
While `stylesheets` are relatively straightforward to use (just ask chatGPT for help), using `stylesheets` sometimes requires a deeper investigation of *shadow DOM* and Bokeh/Panel implementation details.

Learn more about `stylesheets` in the [Apply CSS](../../how_to/styling/apply_css.md) how-to guide.
:::

## Recap

We can finetune the style of our Panel components with [*css*](https://www.w3schools.com/css/):

- Use `styles` to style the *outer container*.
- Use `stylesheets` to style the *inner contents of the container*.

This will ensure our wind turbine data apps are both aesthetically pleasing and user-friendly.

## Resources

### How-to

- [Apply CSS](../../how_to/styling/apply_css.md)
