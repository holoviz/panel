# Simple Outlier App - Declarative API

This app is a complement to the simple app demonstrated in the [Getting Started > Build an app](../../../getting_started/build_app.md) tutorial which utilized the reactive API.

The reactive API approach is very flexible, but it ties your domain-specific code (the parts about sine waves) with your widget display code. That's fine for small, quick projects or projects dominated by visualization code, but what about large-scale, long-lived projects, where the code is used in many different contexts over time, such as in large batch runs, one-off command-line usage, notebooks, and deployed dashboards?  For larger projects like that, it's important to be able to separate the parts of the code that are about the underlying domain (i.e. application or research area) from those that are tied to specific display technologies (such as Jupyter notebooks or web servers).

For such usages, Panel supports objects declared with the separate [Param](http://param.pyviz.org) library, which provides a GUI-independent way of capturing and declaring the parameters of your objects (and dependencies between your code and those parameters), in a way that's independent of any particular application or dashboard technology. For instance, the app in [Getting Started > Build an app](../../../getting_started/build_app.md) can be captured in an object that declares the ranges and values of all parameters, as well as how to generate the plot, independently of the Panel library or any other way of interacting with the object. First, we'll copy the initial steps :


```{pyodide}
import panel as pn
import hvplot.pandas
import numpy as np
import param
import pandas as pd

pn.extension()


csv_file = 'https://raw.githubusercontent.com/holoviz/panel/main/examples/assets/occupancy.csv'
data = pd.read_csv(csv_file, parse_dates=['date'], index_col='date')

data.tail()
```

```{pyodide}
def view_hvplot(avg, highlight):
    return avg.hvplot(height=300, width=400, legend=False) * highlight.hvplot.scatter(
        color="orange", padding=0.1, legend=False
    )

def find_outliers(variable="Temperature", window=30, sigma=10, view_fn=view_hvplot):
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = np.abs(residual) > std * sigma
    return view_fn(avg, avg[outliers])
```

Now, let's implement the declarative API approach:

```{pyodide}
class RoomOccupancy(param.Parameterized):
    variable  = param.Selector(default="Temperature", objects=list(data.columns))
    window    = param.Integer(default=30, bounds=(1, 60))
    sigma     = param.Number(default=10, bounds=(0, 20))

    def view(self):
        return find_outliers(self.variable, self.window, self.sigma, view_fn=view_hvplot)

obj = RoomOccupancy()
obj
```

The `RoomOccupancy` class and the `obj` instance have no dependency on Panel, Jupyter, or any other GUI or web toolkit; they simply declare facts about a certain domain (such as that smoothing requires window and sigma parameters, and that window is an integer greater than 0 and sigma is a positive real number).  This information is then enough for Panel to create an editable and viewable representation for this object without having to specify anything that depends on the domain-specific details encapsulated in `obj`:


```{pyodide}
pn.Column(obj.param, obj.view)
```

To support a particular domain, you can create hierarchies of such classes encapsulating all the parameters and functionality you need across different families of objects, with both parameters and code inheriting across the classes as appropriate, all without any dependency on a particular GUI library or even the presence of a GUI at all.  This approach makes it practical to maintain a large codebase, all fully displayable and editable with Panel, in a way that can be maintained and adapted over time. See the [Attractors Panel app](https://examples.pyviz.org/attractors/attractors_panel.html) ([source](https://github.com/holoviz-topics/examples/tree/main/attractors)) for a more complex illustration of this approach, and the Panel codebase itself for the ultimate demonstration of using Param throughout a codebase!
