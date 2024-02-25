# {octicon}`tools;2em;sd-mr-1` Build an app

At this point you should have [set up your environment and installed Panel](installation.md) so you should be ready to get going.

On this page, we're going to be building a basic interactive application based on [Numpy](https://numpy.org/), [Pandas](https://pandas.pydata.org/) and [hvplot](https://hvplot.holoviz.org/). Please install `hvPlot`.

:::::{tab-set}

::::{tab-item} pip
:sync: pip

```bash
pip install hvplot
```

::::

::::{tab-item} conda
:sync: conda

```bash
conda install -c conda-forge hvplot
```

::::

:::::

If you want to implement this app yourself as you follow along, we recommend starting with a Jupyter notebook. You can also launch the Notebook with JupyterLite on the right.

## Fetch the data

First let's load the [UCI ML dataset](http://archive.ics.uci.edu/ml/datasets/Occupancy+Detection+) that measured the environment in a meeting room:

:::{important}
At first, this website renders code block outputs with limited interactivity, indicated by the <font color="darkgoldenrod">golden</font> border to the left of the output below. By clicking the play button (<svg class="pyodide-run-icon" style="width:32px;height:25px" viewBox="0 0 24 24"> <path stroke="none" fill="#28a745" d="M8,5.14V19.14L19,12.14L8,5.14Z"></path> </svg>) you can activate full interactivity, indicated by a <font color="green">green</font> left-border.
:::

```{pyodide}
import panel as pn
import hvplot.pandas
import pandas as pd
import numpy as np

pn.extension(design='material')

csv_file = ("https://raw.githubusercontent.com/holoviz/panel/main/examples/assets/occupancy.csv")
data = pd.read_csv(csv_file, parse_dates=["date"], index_col="date")

data.tail()
```

## Visualize a subset of the data

Before we utilize Panel, let's write a function that smooths one of our time series and finds the outliers. We will then plot the result using hvplot.

```{pyodide}
def transform_data(variable, window, sigma):
    ''' Calculates the rolling average and the outliers '''
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = np.abs(residual) > std * sigma
    return avg, avg[outliers]

def create_plot(variable="Temperature", window=30, sigma=10):
    ''' Plots the rolling average and the outliers '''
    avg, highlight = transform_data(variable, window, sigma)
    return avg.hvplot(height=300, width=400, legend=False) * highlight.hvplot.scatter(
        color="orange", padding=0.1, legend=False
    )
```

We can now call our `create_plot` function with specific parameters to get a plot with a single set of parameters.

```{pyodide}
create_plot(variable='Temperature', window=20, sigma=10)
```

It works! But now we want explore how values for `window` and `sigma` affect the plot. We could reevaluate the above cell a lot of times, but that would be a slow and painful process. Instead, let's use Panel to quickly add some interactive controls and quickly determine how different parameter values impact the output.

## Explore parameter space

Let's create some Panel slider widgets for the range of parameter values that we want to explore.

```{pyodide}
variable_widget = pn.widgets.Select(name="variable", value="Temperature", options=list(data.columns))
window_widget = pn.widgets.IntSlider(name="window", value=30, start=1, end=60)
sigma_widget = pn.widgets.IntSlider(name="sigma", value=10, start=0, end=20)
```

Now that we have a function and some widgets, let's link them together so that updates to the widgets rerun the function. One easy way to create this link in Panel is with `pn.bind`:

```{pyodide}
bound_plot = pn.bind(create_plot, variable=variable_widget, window=window_widget, sigma=sigma_widget)
```

Once you have bound the widgets to the function's arguments you can lay out the resulting `bound_plot` component along with the `widget` components using a Panel layout such as `Column`:

```{pyodide}
first_app = pn.Column(variable_widget, window_widget, sigma_widget, bound_plot)

first_app.servable()
```

As long as you have a live Python process running, dragging these widgets will trigger a call to the `create_plot` callback function, evaluating it for whatever combination of parameter values you select and displaying the results.

## Next Steps

Now that we have given you a taste of how easy it is to build a little application in Panel, it's time to introduce you to some of the [core concepts](core_concepts.md) behind Panel.
