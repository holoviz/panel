# Aligning Content

Welcome to our tutorial on aligning content in Panel! Let's dive into exploring various alignment, margin, and spacing options to make your content look polished and visually appealing.

## Understand Alignment Options

In this tutorial, we'll delve into three key aspects:

- **Alignment**: You can `align` content horizontally and vertically within a container, choosing from options like `'start'`, `'center'`, or `'end'`.
- **Spacer Component**: Utilize `Spacer` components to adjust alignment or add space between content.
- **Margin**: Fine-tune alignment by adding `margin`s to content elements.

Let's jump in and explore these concepts in action!

## Align a Button

Let's start by aligning a button horizontally within a container. Run the code below:

```{pyodide}
import panel as pn

pn.extension()

pn.Column(
    pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=150, sizing_mode="scale_width"),
    pn.widgets.Button(name="Stop the Turbine", icon="hand-stop",),
    sizing_mode="fixed", width=400, height=400, styles={"border": "1px solid black"}
).servable()
```

Now, let's align the button to the center horizontally using three different techniques:

- Using the `align` parameter
- Leveraging `Spacer` components
- Adjusting `margin` values

Feel free to run the code snippets for each technique below and observe the changes.

:::::{tab-set}

::::{tab-item} Align

```{pyodide}
import panel as pn

pn.extension()

pn.Column(
    pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=150, sizing_mode="scale_width"),
    pn.widgets.Button(name="Stop the Turbine", icon="hand-stop", align="center"),
    sizing_mode="fixed", width=400, height=400, styles={"border": "1px solid black"}
).servable()
```

You can use a single value or a 2-tuple (horizontal, vertical) with the `align` parameter.

::::

::::{tab-item} Spacer

```{pyodide}
import panel as pn

pn.extension()

pn.Column(
    pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=150, sizing_mode="scale_width"),
    pn.Row(
        pn.Spacer(sizing_mode="stretch_width"),
        pn.widgets.Button(name="Stop the Turbine", icon="hand-stop"),
        pn.Spacer(sizing_mode="stretch_width")
    ),
    sizing_mode="fixed", width=400, height=400, styles={"border": "1px solid black", "border-radius": "5px"}
).servable()
```

::::

::::{tab-item} Margin

```{pyodide}
import panel as pn

pn.extension()

margin = int((400-147)/2) # The Button is 147 pixels wide

pn.Column(
    pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=150, sizing_mode="scale_width"),
    pn.widgets.Button(name="Stop the Turbine", icon="hand-stop", margin=(5,margin)),
    sizing_mode="fixed", width=400, height=400, styles={"border": "1px solid black"}
).servable()
```

:::{tip}
The `margin` parameter can take a single value, a 2-tuple (top/bottom, left/right), or a 4-tuple (top, right, bottom, left).
:::

::::

:::::

:::{tip}
As a rule of thumb:

- Use `align` to adjust the overall alignment.
- Use `Spacer` for broader alignment or spacing adjustments when `align` isn't sufficient.
- Use `margin` for fine-tuning alignment or adding fixed-size spacing.
:::

## Exercise: Align Cards

Let's practice aligning cards within a container. Run the code snippet below:

```{pyodide}
import panel as pn

pn.extension()

image = pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", height=150, sizing_mode="scale_width")

card1 = pn.Card(image, title='Turbine 1', width=200)
card2 = pn.Card(image, title='Turbine 2', width=200)

pn.Column(
    card1, card2,
    sizing_mode="fixed", width=400, height=400, styles={"border": "1px solid black"}
).servable()
```

Your task is to align each card in the center of its respective vertical half. There are many possible solutions, but your solution should resemble the image below:

![Align Cards Solution](../../_static/images/align-cards-solution.png)

:::::{dropdown} Solutions

::::{tab-set}

:::{tab-item} Align + Spacer

```{pyodide}
import panel as pn

pn.extension()

image = pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", sizing_mode="scale_both")

card1 = pn.Card(image, title='Turbine 1', height=150, width=200, align="center")
card2 = pn.Card(image, title='Turbine 2', height=150, width=200, align="center")
spacer = pn.Spacer(height=33)

pn.Column(
    spacer, card1, spacer, card2,
    sizing_mode="fixed", width=400, height=400, styles={"border": "1px solid black"}
).servable()
```

:::

:::{tab-item} Align + Margin

```{pyodide}
import panel as pn

pn.extension()

image = pn.pane.PNG("https://assets.holoviz.org/panel/tutorials/wind_turbine.png", sizing_mode="scale_both")

card1 = pn.Card(image, title='Turbine 1', height=150, width=200, align="center", margin=(33,0,17,0))
card2 = pn.Card(image, title='Turbine 2', height=150, width=200, align="center", margin=(16,0,33,0))

pn.Column(
    card1, card2,
    sizing_mode="fixed", width=400, height=400, styles={"border": "1px solid black"}
).servable()
```

:::

::::

:::::

## Recap

In this tutorial, we've explored various alignment and spacing options for content in Panel:

- **Alignment**: Adjust content `align`meant horizontally and vertically within a container.
- **Spacer Component**: Utilize `Spacer` components to align or add space between content elements.
- **Margin**: Fine-tune alignment or add space between content using `margin`.

Now, you're equipped with the knowledge to beautifully align and space your content in Panel!

## References

### How-to Guides

- [Align Components](../../how_to/layout/align.md)
