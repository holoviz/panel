# Plot Viewer

```{pyodide}
import param
import panel as pn

from bokeh.sampledata.iris import flowers
from panel.viewable import Viewer

pn.extension(template='fast')
import hvplot.pandas
```

This example demonstrates the use of a `Viewer` class to build a reactive app. It uses the [iris dataset](https://en.wikipedia.org/wiki/Iris_flower_data_set) which is a standard example used to illustrate machine-learning and visualization techniques.

We will start by using the dataframe with these five features and then create a `Selector` parameter to develop menu options for different input features. Later we will define the core plotting function in a `plot` method and define the layout in the `__panel__` method of the `IrisDashboard` class.

The `plot` method watches the `X_variable` and `Y_variable` using the `param.depends` [decorator](https://www.google.com/search?q=python+decorator). The `plot` method plots the features selected for `X_variable` and `Y_variable` and colors them using the `species` column.

```{pyodide}
inputs = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']

class IrisDashboard(Viewer):
    X_variable = param.Selector(objects=inputs, default=inputs[0])
    Y_variable = param.Selector(objects=inputs, default=inputs[1])

    @param.depends('X_variable', 'Y_variable')
    def plot(self):
        return flowers.hvplot.scatter(x=self.X_variable, y=self.Y_variable, by='species').opts(height=600)

    def __panel__(self):
        return pn.Row(
            pn.Param(self, width=300, name="Plot Settings"),
            self.plot
        )

IrisDashboard(name='Iris_Dashboard').servable()
```
