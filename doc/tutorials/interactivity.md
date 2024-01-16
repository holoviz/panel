# Interactivity

:::{note} Tutorial 3. **Interactivity**
:icon: false

In the previous section we learned a lot about Param, which underlies not only the core architecture of Panel itself but also provides the foundation to adding interactivity to your applications. In this section we will discover how to leverage Parameters and dependencies on parameters to add interactivity. In particular we will focus on implementing interactivity through reactivity, rather than the more imperative style of programming you might be used to from other UI frameworks.

By the end of this tutorial you should have learned:

- How to use both declarative and imperative APIs to achieve interactivity
- How to develop both functional and class based interactive apps

:::

```{pyodide}
import pandas as pd
import param
import panel as pn

pn.extension('tabulator')
```

## Declarative vs. Imperative programming

To build an interactive component in Panel we have two options, either we define callbacks that perform explicit actions, e.g. "when this widget changes update this component", or we declare reactive functions, methods or expressions that returns a specific output given some input and automatically manage the state.

Let's look at what this looks like in practice by building a simple app that allows us to select a subset of columns to display in a table.

### Imperative

In both cases we start by loading our data and then defining a widget that will allow us to interact with the data:

```{pyodide}
data_url = 'https://datasets.holoviz.org/windturbines/v1/windturbines.parq'

turbines = pd.read_parquet(data_url)

cols = pn.widgets.MultiChoice(
    options=turbines.columns.to_list(), value=['p_name', 't_state', 't_county', 'p_year', 't_manu', 'p_cap'],
    width=500, height=120, name='Columns'
)
```

In the imperative approach we use `.param.watch` to set up a callback that will update the data when the widget changes:

```{pyodide}
table = pn.widgets.Tabulator(turbines[cols.value], page_size=5)

def update_data(event):
    table.value = turbines[event.new]

cols.param.watch(update_data, 'value')

pn.Column(cols, table)
```

## Declarative

The declarative and reactive approach differs in that we only have to declare what we want to display and Panel takes care of the actual mechanics of updating the table for us:

```{pyodide}
dfrx = pn.rx(turbines)[cols]

pn.Column(cols, pn.widgets.Tabulator(dfrx, page_size=5))
```

Note how we pass the reactive DataFrame to the `Tabulator` widget. This goes back to the concept of passing references, which Param and Panel will resolve. Valid references include:

- `param.Parameter()`
- `param.rx(...)`
- `pn.bind(func)`
- `pn.widgets.Widget()`

### Exercise

Extend the app below by adding widgets that will let you to filter the data by year (`p_year`) and capacity (`p_cap`):

:::{note} Hint
:class: dropdown

```python
 You can filter a reactive DataFrame in the same way as a regular DataFrame.
```
:::

Now briefly consider how this would look if you wrote this application using the imperative style of programming.

## Function vs. class based

Reactive functions and expressions based on `pn.bind` and `pn.rx` provide an excellent entrypoint when writing dynamic UIs. However as soon as we want to track state or have many consumers of the output it can be hard to keep track. This is where classes come in.

If you remember the [Param section](./01_Param.ipynb) a `Parameterized` class allows you to encapsulate state as parameters and those parameters can then be passed around to set up interactivity. Let's revive our `DataExplorer` class from that earlier lesson and see how we can structure a filtering application like above:

```{pyodide}
import param

from panel.viewable import Viewer

class DataExplorer(Viewer):

    data = param.DataFrame(doc="Stores a DataFrame to explore")

    columns = param.ListSelector(default=['p_name', 't_state', 't_county', 'p_year', 't_manu', 'p_cap'])

    year = param.Range(default=(1981, 2022), bounds=(1981, 2022))

    capacity = param.Range(default=(0, 1100), bounds=(0, 1100))

    def __init__(self, **params):
        super().__init__(**params)
        self.param.columns.objects = self.data.columns.to_list()

    @param.depends('data', 'columns', 'year', 'capacity')
    def filtered_data(self):
        df = self.data
        return df[
            df.p_year.between(*self.year) &
            df.p_cap.between(*self.capacity)
        ][self.columns]

    def __panel__(self):
        return pn.Column(
            pn.Row(
                pn.widgets.MultiChoice.from_param(self.param.columns, width=400),
                pn.Column(self.param.year, self.param.capacity)
            ),
            pn.widgets.Tabulator(
                self.filtered_data, page_size=10, pagination='remote'
            )
        )

DataExplorer(data=turbines)
```

As you can see `param.depends` allows us to set up a method that depends on specific parameters on the class (much like `pn.bind`) and then use that method as a proxy for the filtered data. An alternative approach would be to create a parameter to store the filtered data that runs every time one of the dependencies change.

```{pyodide}
class DataExplorer(Viewer):

    data = param.DataFrame(doc="Stores a DataFrame to explore")

    columns = param.ListSelector(default=['p_name', 't_state', 't_county', 'p_year', 't_manu', 'p_cap'])

    year = param.Range(default=(1981, 2022), bounds=(1981, 2022))

    capacity = param.Range(default=(0, 1100), bounds=(0, 1100))

    filtered = param.DataFrame(doc="Stores the filtered DataFrame")

    @param.depends('data', 'year', 'capacity', 'columns', watch=True, on_init=True)
    def _update_filtered(self):
        self.filtered = self.data[
            self.data.p_year.between(*self.year) &
            self.data.p_cap.between(*self.capacity)
        ][self.columns]

    @param.depends('filtered')
    def _table(self):
        pass

    @param.depends('filtered')
    def _figure(self):
        pass

DataExplorer(data=turbines, year=(2021, 2022), capacity=(1000, 1100)).filtered.head()
```

The difference between these approaches is that in the first case the `filtered_data` method acts as a declarative reference which is evaluated when needed, while `_update_filtered` runs whenever any of the dependencies change in an imperative way, i.e. it is just an easy way to write a callback. The benefit of storing the filtered data is that multiple consumers can now have access to it.

There are no hard rules when to use which approach, imperative approaches are very explicit about state management often making them easier to reason about than a reactive approach where the state management is hidden or controlled via helpers such as `@pn.cache`.

### Exercise

Write an app that allows filtering the DataFrame and display both a table and a plot and caches the data on an intermediate parameter. You can use any plotting library you want.

:::{note} Hint
:class: dropdown

```python
import hvplot.pandas
plot = turbines.hvplot.points('easting', 'northing', tiles='ESRI', rasterize=True)
```
:::
