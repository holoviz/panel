# {octicon}`mortar-board;2em;sd-mr-1` Build an App

By now, you should have [set up your environment and installed Panel](installation.md), so you're all set to dive in!

In this section, we'll walk through creating a basic interactive application using [NumPy](https://numpy.org/), [Pandas](https://pandas.pydata.org/), and [hvPlot](https://hvplot.holoviz.org/). If you haven't installed `hvPlot` yet, you can do so with `pip install hvplot` or `conda install -c conda-forge hvplot`.

Let's envision what our app will look like:

![Getting Started App](../_static/images/getting_started_app.png)

If you're eager to roll up your sleeves and build this app alongside us, we recommend starting with a Jupyter notebook. You can also run the code directly in the docs or launch the Notebook with JupyterLite on the right.

:::{important}
Initially, the code block outputs on this website offer limited interactivity, indicated by the <font color="darkgoldenrod">golden</font> border to the left of the output below. By clicking the play button (<svg class="pyodide-run-icon" style="width:32px;height:25px" viewBox="0 0 24 24"> <path stroke="none" fill="#28a745" d="M8,5.14V19.14L19,12.14L8,5.14Z"></path> </svg>), you can activate full interactivity, marked by a <font color="green">green</font> left-border.
:::

## Fetching the Data

First, let's import the necessary dependencies and define some variables:

```{pyodide}
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn

PRIMARY_COLOR = "#0072B5"
SECONDARY_COLOR = "#B54300"
CSV_FILE = (
    "https://raw.githubusercontent.com/holoviz/panel/main/examples/assets/occupancy.csv"
)
```

Next, we'll import the Panel JavaScript dependencies using `pn.extension(...)`. For a visually appealing and responsive user experience, we'll set the `design` to `"material"` and the `sizing_mode` to `stretch_width`:

```{pyodide}
pn.extension(design="material", sizing_mode="stretch_width")
```

Now, let's load the [UCI ML dataset](http://archive.ics.uci.edu/dataset/357/occupancy+detection) that measured the environment in a meeting room. We'll speed up our application by caching (`@pn.cache`) the data across users:

```{pyodide}
@pn.cache
def get_data():
  return pd.read_csv(CSV_FILE, parse_dates=["date"], index_col="date")

data = get_data()

data.tail()
```

## Visualizing a Subset of the Data

Before diving into Panel, let's create a function that smooths one of our time series and identifies outliers. Then, we'll plot the result using hvPlot:

```{pyodide}
def transform_data(variable, window, sigma):
    """Calculates the rolling average and identifies outliers"""
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = np.abs(residual) > std * sigma
    return avg, avg[outliers]


def get_plot(variable="Temperature", window=30, sigma=10):
    """Plots the rolling average and the outliers"""
    avg, highlight = transform_data(variable, window, sigma)
    return avg.hvplot(
        height=300, legend=False, color=PRIMARY_COLOR
    ) * highlight.hvplot.scatter(color=SECONDARY_COLOR, padding=0.1, legend=False)
```

Now, we can call our `get_plot` function with specific parameters to obtain a plot with a single set of parameters:

```{pyodide}
get_plot(variable='Temperature', window=20, sigma=10)
```

Great! Now, let's explore how different values for `window` and `sigma` affect the plot. Instead of reevaluating the above cell multiple times, let's use Panel to add interactive controls and quickly visualize the impact of different parameter values.

## Exploring the Parameter Space

Let's create some Panel slider widgets to explore the range of parameter values:

```{pyodide}
variable_widget = pn.widgets.Select(name="variable", value="Temperature", options=list(data.columns))
window_widget = pn.widgets.IntSlider(name="window", value=30, start=1, end=60)
sigma_widget = pn.widgets.IntSlider(name="sigma", value=10, start=0, end=20)
```

Now, let's link these widgets to our plotting function so that updates to the widgets rerun the function. We can achieve this easily in Panel using `pn.bind`:

```{pyodide}
bound_plot = pn.bind(
    get_plot, variable=variable_widget, window=window_widget, sigma=sigma_widget
)
```

Once we've bound the widgets to the function's arguments, we can layout the resulting `bound_plot` component along with the `widgets` using a Panel layout such as `Column`:

```{pyodide}
widgets = pn.Column(variable_widget, window_widget, sigma_widget, sizing_mode="fixed", width=300)
pn.Column(widgets, bound_plot)
```

As long as you have a live Python process running, dragging these widgets will trigger a call to the `get_plot` callback function, evaluating it for whatever combination of parameter values you select and displaying the results.

## Serving the Notebook

We'll organize our components in a nicely styled template (`MaterialTemplate`) and mark it `.servable()` to add it to our served app:

```python
pn.template.MaterialTemplate(
    site="Panel",
    title="Getting Started App",
    sidebar=[variable_widget, window_widget, sigma_widget],
    main=[bound_plot],
).servable(); # The ; is needed in the notebook to not display the template. Its not needed in a script
```

Save the notebook with the name `app.ipynb`.

Finally, we'll serve the app with:

```bash
panel serve app.ipynb --autoreload
```

Now, open the app in your browser at [http://localhost:5006/app](http://localhost:5006/app).

It should look like this:

![Getting Started App](../_static/images/getting_started_app.png)

:::{tip}

If you prefer developing in a Python Script using an editor, you can copy the code into a file `app.py` and serve it.

```bash
panel serve app.py --autoreload
```

:::

## What's Next?

Now that you've experienced how easy it is to build a simple application in Panel, it's time to delve into some of the [core concepts](core_concepts.md) behind Panel.
