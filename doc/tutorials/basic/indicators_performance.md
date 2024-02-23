# Display Performance with Indicators

Welcome to our tutorial on displaying the performance of wind turbines using Panel's [indicators](https://panel.holoviz.org/reference/index.html#indicators)! Let's delve into visualizing the key metrics of our wind turbines in an engaging and insightful manner.

## Explore Indicators

In this tutorial, we'll explore various indicators offered by Panel to showcase the performance metrics:

- **Current Performance**: Utilize the [`Number`](../../reference/indicators/Number.ipynb) indicator to display the current performance.
- **Trending Performance**: Employ the [`Trend`](../../reference/indicators/Trend.ipynb) indicator to showcase the trending performance over time.

For a comprehensive list of indicators and their detailed reference guides, you can always refer to the [Indicators Section](https://panel.holoviz.org/reference/index.html#indicators) in the [Component Gallery](../../reference/index.md).

:::{note}
Throughout this tutorial, whenever we refer to "running the code," you can execute it directly in the Panel docs using the green *run* button, in a notebook cell, or within a file named `app.py` served with `panel serve app.py --autoreload`.
:::

## Display a Number

Let's start by displaying the wind speed using the `Number` indicator:

```{pyodide}
import panel as pn

pn.extension()

pn.indicators.Number(
    name="Wind Speed",
    value=8.6,
    format="{value} m/s",
    colors=[(10, "green"), (100, "red")],
).servable()
```

:::{note}
Adding `.servable()` to the `Number` indicator incorporates it into the app served by `panel serve app.py --autoreload`. Note that it's not necessary for displaying the indicator in a notebook.
:::

Feel free to tweak the `value` from `8.6` to `11.4` and observe the color change to *red*.

## Display a Trend

Next, let's visualize the hourly average wind speed trend:

```{pyodide}
import panel as pn
import numpy as np

pn.extension()

def get_wind_speeds(n):
    # Replace this with your own wind speed data source
    return {"x": np.arange(n), "y": 8 + np.random.randn(n)}

pn.indicators.Trend(
    name="Wind Speed (m/s, hourly avg.)",
    data=get_wind_speeds(24),
    width=500,
    height=300,
).servable()
```

Experiment by adjusting the `height` parameter from `300` to `500`.

For more detailed insights into the `Trend` indicator, take a moment to explore its [reference guide](../../reference/indicators/Trend.ipynb). Trust us, it's worth it!

## Discover More Indicators

Explore all indicators and their respective reference guides in the [Indicators Section](https://panel.holoviz.org/reference/index.html#indicators) of the [Component Gallery](../../reference/index.md).

## Recap

In this tutorial, we've embarked on visualizing the performance metrics of wind turbines using Panel's versatile indicators:

- Leveraged the [`Number`](../../reference/indicators/Number.ipynb) indicator to display current performance.
- Utilized the [`Trend`](../../reference/indicators/Trend.ipynb) indicator to showcase trending performance over time.

Remember, there's a plethora of indicators waiting for you to explore in the [Indicators Section](https://panel.holoviz.org/reference/index.html#indicators) of the [Component Gallery](../../reference/index.md). Keep experimenting and uncovering new insights! 🚀
