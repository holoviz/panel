# Interactivity

In the previous sections, we delved into [Param](https://param.holoviz.org/), which not only forms the core architecture of Panel but also serves as the foundation for adding interactivity to your applications. This section explores how to leverage Parameters and their dependencies to incorporate interactivity. We'll focus on implementing interactivity through reactivity, departing from the more imperative style of programming commonly found in other UI frameworks.

By the end of this tutorial, you'll learn:

- How to utilize both declarative and imperative APIs for interactivity
- How to develop both functional and class-based interactive apps

## Imperative vs Declarative Programming

To create an interactive component in Panel, we have two approaches: defining callbacks for explicit actions or declaring reactive functions, methods, or expressions that automatically manage state changes.

:::{tip}

For users of all skill levels, we recommend employing the Declarative Programming approach as it enhances code maintainability and efficiency.

:::

Let's explore these approaches by building a simple app that enables us to select a subset of columns to display in a table.

### Imperative

We begin by loading our data and defining a widget for interacting with it:

```{pyodide}
import panel as pn
import pandas as pd

pn.extension("tabulator")

data_url = 'https://assets.holoviz.org/panel/tutorials/turbines.csv.gz'

turbines = pn.cache(pd.read_csv)(data_url)

cols = pn.widgets.MultiChoice(
    options=turbines.columns.to_list(), value=['p_name', 't_state', 't_county', 'p_year', 't_manu', 'p_cap'],
    width=500, height=100, name='Columns'
)
```

In the imperative approach, we use `.param.watch` to set up a callback that updates the data when the widget changes:

```{pyodide}
table = pn.widgets.Tabulator(turbines[cols.value], page_size=5, pagination="remote")

def update_data(event):
    table.value = turbines[event.new]

cols.param.watch(update_data, 'value')

pn.Column(cols, table).servable()
```

### Declarative

The declarative and reactive approach involves declaring what we want to display, leaving Panel to handle the mechanics of updating the table:

```{pyodide}
dfrx = pn.rx(turbines)[cols]

pn.Column(cols, pn.widgets.Tabulator(dfrx, page_size=5, pagination="remote")).servable()
```

Note how we pass the reactive DataFrame `dfrx` to the `Tabulator` widget. This aligns with the concept of passing references, which Param and Panel resolve. Valid references include:

- `param.Parameter()`
- `param.rx(...)`
- `pn.bind(...)`/ `@pn.depends`
- `pn.widgets.Widget()`

### Exercise: Add more Widgets

Enhance the app by adding widgets to filter the data by year (`p_year`) and capacity (`p_cap`):

:::{hint}

You can filter a reactive DataFrame in the same way as a regular DataFrame.

:::

:::{dropdown} Solution: Declarative (Recommended)

```{pyodide}
import pandas as pd
import panel as pn

pn.extension("tabulator")

data_url = "https://assets.holoviz.org/panel/tutorials/turbines.csv.gz"

turbines = pn.cache(pd.read_csv)(data_url)

cols = pn.widgets.MultiChoice(
    options=turbines.columns.to_list(),
    value=["p_name", "t_state", "t_county", "p_year", "t_manu", "p_cap"],
    width=500,
    height=100,
    name="Columns",
)
p_year_options = sorted(int(year) for year in turbines.p_year.unique() if not pd.isna(year))
p_year = pn.widgets.Select(value=max(p_year_options), options=p_year_options, name="Year")

p_cap_bounds = (turbines.p_cap.min(), turbines.p_cap.max())
p_cap = pn.widgets.RangeSlider(value=p_cap_bounds, start=p_cap_bounds[0], end=p_cap_bounds[1])

dfrx = pn.rx(turbines)
dfrx = dfrx[
    (dfrx.p_year == p_year)
    & (dfrx.p_cap.between(p_cap.param.value_start, p_cap.param.value_end))
][cols]
pn.Column(
    cols, p_year, p_cap, pn.widgets.Tabulator(dfrx, pagination="remote", page_size=5)
).servable()
```

:::

:::{dropdown} Solution: Imperative (Not recommended)

```{pyodide}
import pandas as pd
import panel as pn

pn.extension("tabulator")

data_url = "https://assets.holoviz.org/panel/tutorials/turbines.csv.gz"

turbines = pn.cache(pd.read_csv)(data_url)

cols = pn.widgets.MultiChoice(
    options=turbines.columns.to_list(),
    value=["p_name", "t_state", "t_county", "p_year", "t_manu", "p_cap"],
    width=500,
    height=100,
    name="Columns",
)
p_year_options = sorted(
    int(year) for year in turbines.p_year.unique() if not pd.isna(year)
)
p_year = pn.widgets.Select(
    value=max(p_year_options), options=p_year_options, name="Year"
)

p_cap_bounds = (turbines.p_cap.min(), turbines.p_cap.max())
p_cap = pn.widgets.RangeSlider(
    value=p_cap_bounds, start=p_cap_bounds[0], end=p_cap_bounds[1], name="Capacity"
)

table = pn.widgets.Tabulator(turbines[cols.value], page_size=5, pagination="remote")


def update_data(event):
    value = turbines[
        (turbines.p_year == p_year.value)
        & (turbines.p_cap.between(p_cap.value_start, p_cap.value_end))
    ][cols.value]

    table.value = value


cols.param.watch(update_data, "value")
p_year.param.watch(update_data, "value")
p_cap.param.watch(update_data, "value")

pn.Column(cols, p_year, p_cap, table).servable()
```

:::

## Function vs. Class-based

Reactive functions and expressions based on `pn.rx` or `pn.bind` provide an excellent entry point for writing dynamic UIs. However, when we need to track state or have many consumers of the output, it can be challenging to manage. This is where `Parameterized` classes come in handy.

If you recall the [Reactive Parameters Section](parameters.md), a `Parameterized` class enables you to encapsulate state as parameters, which can then be passed around to set up interactivity.

:::{tip}

The class-based approach is recommended for larger, more complex applications.

:::

## Making the Class-Based Approach Efficient

Let's revisit our `DataExplorer` class from the previous lesson and see how we can structure a filtering application like before:

```{pyodide}
import pandas as pd
import panel as pn
import param
from panel.viewable import Viewer

pn.extension("tabulator")

data_url = "https://assets.holoviz.org/panel/tutorials/turbines.csv.gz"

turbines = pn.cache(pd.read_csv)(data_url)


class DataExplorer(Viewer):
    data = param.DataFrame(doc="Stores a DataFrame to explore")

    columns = param.ListSelector(
        default=["p_name", "t_state", "t_county", "p_year", "t_manu", "p_cap"]
    )

    year = param.Range(default=(1981, 2022), bounds=(1981, 2022))

    capacity = param.Range(default=(0, 1100), bounds=(0, 1100))

    def __init__(self, **params):
        super().__init__(**params)
        self.param.columns.objects = self.data.columns.to_list()

    @param.depends("data", "columns", "year", "capacity")
    def filtered_data(self):
        df = self.data
        return df[df.p_year.between(*self.year) & df.p_cap.between(*self.capacity)][
            self.columns
        ]

    @param.depends('filtered_data')
    def number_of_rows(self):
        return f"Rows: {len(self.filtered_data())}"

    def __panel__(self):
        return pn.Column(
            pn.Row(
                pn.widgets.MultiChoice.from_param(self.param.columns, width=400),
                pn.Column(self.param.year, self.param.capacity),
            ),
            self.number_of_rows,
            pn.widgets.Tabulator(self.filtered_data, page_size=10, pagination="remote"),
        )


DataExplorer(data=turbines).servable()
```

As you can see, `param.depends` allows us to set up a method that depends on specific parameters of the class (much like `pn.bind`) and then use that method as a proxy for the filtered data. If you observe the execution flow, you'll notice that the `filtered_data` method is executed twice whenever one of `data`, `columns`, `year`, or `capacity` is changed. You can avoid this inefficiency by using `pn.cache`.

An alternative and slightly more efficient approach would be to create a parameter to store the filtered data and update it every time one of the dependencies changes.

```{pyodide}
import pandas as pd
import panel as pn
import param
from panel.viewable import Viewer

pn.extension("tabulator")

data_url = "https://assets.holoviz.org/panel/tutorials/turbines.csv.gz"

turbines = pn.cache(pd.read_csv)(data_url)


class DataExplorer(Viewer):
    data = param.DataFrame(doc="Stores a DataFrame to explore")

    columns = param.ListSelector(
        default=["p_name", "t_state", "t_county", "p_year", "t_manu", "p_cap"]
    )

    year = param.Range(default=(1981, 2022), bounds=(1981, 2022))

    capacity = param.Range(default=(0, 1100), bounds=(0, 1100))

    filtered_data = param.DataFrame(doc="Stores the filtered DataFrame")

    def __init__(self, **params):
        super().__init__(**params)
        self.param.columns.objects = self.data.columns.to_list()

    @param.depends("data", "columns", "year", "capacity", watch=True, on_init=True)
    def _update_filtered_data(self):
        df = self.data
        self.filtered_data=df[df.p_year.between(*self.year) & df.p_cap.between(*self.capacity)][
            self.columns
        ]

    @param.depends('filtered_data')
    def number_of_rows(self):
        return f"Rows: {len(self.filtered_data)}"

    def __panel__(self):
        return pn.Column(
            pn.Row(
                pn.widgets.MultiChoice.from_param(self.param.columns, width=400),
                pn.Column(self.param.year, self.param.capacity),
            ),
            self.number_of_rows,
            pn.widgets.Tabulator(self.param.filtered_data, page_size=10, pagination="remote"),
        )

DataExplorer(data=turbines).servable()
```

Storing the `filtered_data` has the benefit that multiple consumers can now access it without recalculating it.

We can also combine the class-based approach with `pn.rx` to achieve an efficient solution:

```{pyodide}
import pandas as pd
import panel as pn
import param
from panel.viewable import Viewer

pn.extension("tabulator")

data_url = "https://assets.holoviz.org/panel/tutorials/turbines.csv.gz"

turbines = pn.cache(pd.read_csv)(data_url)


class DataExplorer(Viewer):
    data = param.DataFrame(doc="Stores a DataFrame to explore")

    columns = param.ListSelector(
        default=["p_name", "t_state", "t_county", "p_year", "t_manu", "p_cap"]
    )

    year = param.Range(default=(1981, 2022), bounds=(1981, 2022))

    capacity = param.Range(default=(0, 1100), bounds=(0, 1100))

    filtered_data = param.Parameter()

    number_of_rows = param.Parameter()

    def __init__(self, **params):
        super().__init__(**params)
        self.param.columns.objects = self.data.columns.to_list()

        dfrx = self.param.data.rx()

        p_year_min = self.param.year.rx().rx.pipe(lambda x: x[0])
        p_year_max = self.param.year.rx().rx.pipe(lambda x: x[1])
        p_cap_min = self.param.capacity.rx().rx.pipe(lambda x: x[0])
        p_cap_max = self.param.capacity.rx().rx.pipe(lambda x: x[1])

        self.filtered_data = dfrx[
            dfrx.p_year.between(p_year_min, p_year_max)
            & dfrx.p_cap.between(p_cap_min, p_cap_max)
        ][self.param.columns]

        self.number_of_rows = pn.rx("Rows: {len_df}").format(len_df=pn.rx(len)(dfrx))

    def __panel__(self):
        return pn.Column(
            pn.Row(
                pn.widgets.MultiChoice.from_param(self.param.columns, width=400),
                pn.Column(self.param.year, self.param.capacity),
            ),
            self.number_of_rows,
            pn.widgets.Tabulator(self.filtered_data, page_size=10, pagination="remote"),
        )


DataExplorer(data=turbines).servable()
```

:::{tip}

- If your dependent function (`@pn.depends`) will only be executed once per update, the first approach is recommended as it's simple to implement and reason about.
- If not, we recommend using the second approach (`@pn.depends` with `watch=True`) or the third approach (`pn.rx`) because it's much easier to implement efficiently.

:::

### Exercise: Add a Plot

Write an app that allows filtering the DataFrame and displays both a table and a plot, caching the data on an intermediate parameter. You can use any plotting library you want.

:::{hint}

```python
import hvplot.pandas
plot = turbines.hvplot.hist("p_cap", height=400)
```

:::

:::{dropdown} Solution

```{pyodide}
import hvplot.pandas
import pandas as pd
import panel as pn
import param
from panel.viewable import Viewer

pn.extension("tabulator")

data_url = "https://assets.holoviz.org/panel/tutorials/turbines.csv.gz"

turbines = pn.cache(pd.read_csv)(data_url)


class DataExplorer(Viewer):
    data = param.DataFrame(doc="Stores a DataFrame to explore")

    columns = param.ListSelector(
        default=["p_name", "t_state", "t_county", "p_year", "t_manu", "p_cap"]
    )

    year = param.Range(default=(1981, 2022), bounds=(1981, 2022))

    capacity = param.Range(default=(0, 1100), bounds=(0, 1100))

    filtered_data = param.DataFrame(doc="Stores the filtered DataFrame")

    def __init__(self, **params):
        super().__init__(**params)
        self.param.columns.objects = self.data.columns.to_list()

    @param.depends("data", "year", "capacity", watch=True, on_init=True)
    def _update_filtered_data(self):
        df = self.data
        self.filtered_data = df[
            df.p_year.between(*self.year) & df.p_cap.between(*self.capacity)
        ]

    @param.depends("filtered_data", "columns")
    def table(self):
        return self.filtered_data[self.columns]

    @param.depends("filtered_data")
    def plot(self):
        return self.filtered_data.hvplot.hist("p_cap", height=400)

    def __panel__(self):
        return pn.Column(
            pn.Row(
                pn.widgets.MultiChoice.from_param(self.param.columns, width=400),
                pn.Column(self.param.year, self.param.capacity),
            ),
            pn.widgets.Tabulator(self.table, page_size=10, pagination="remote"),
            pn.pane.HoloViews(self.plot),
        )


DataExplorer(data=turbines).servable()
```

:::

### Recap

In this tutorial, we explored how to build an efficient filtering application using Panel. The focus was on optimizing the class-based approach to handle filtering operations on a DataFrame efficiently.

#### Key Concepts Covered

1. **Class-Based Approach:**
   - We started by revisiting a class-based approach for building interactive apps in Panel. This involved creating a `DataExplorer` class to handle filtering operations on a DataFrame.

2. **Parameter Dependencies:**
   - Utilizing `param.depends`, we established dependencies between different parameters and methods within the `DataExplorer` class. This allowed us to trigger updates to specific methods whenever the parameters changed.

3. **Imperative vs Declarative Programming:**
   - We discussed two programming paradigms for building interactive components in Panel:
     - **Imperative:** Defining explicit callbacks to perform actions based on widget changes.
     - **Declarative:** Using reactive functions or expressions to automatically manage state updates based on input changes. We recommended the declarative approach for its maintainability and efficiency.

4. **Efficiency Considerations:**
   - We explored the importance of efficiency when dealing with large datasets or complex filtering operations. Inefficient code can lead to unnecessary recalculations and decreased performance.

5. **Improving Efficiency:**
   - To enhance efficiency, we explored three approaches:
     - Using `pn.cache` to cache the filtered data.
     - Storing the filtered data as a parameter and updating it when dependencies change.
     - Combining the class-based approach with `pn.rx` for reactive programming.

#### Key Takeaways

- **Imperative vs Declarative Programming:** Understanding the difference between imperative and declarative programming paradigms helps in choosing the most suitable approach for building interactive components in Panel.

- **Parameter Dependencies:** Establishing dependencies between parameters and methods using `param.depends` is fundamental for reactive updates in Panel apps.

- **Efficiency is Crucial:** When building interactive applications, especially with large datasets, prioritizing efficiency is essential to ensure optimal performance.

- **Caching and Storing Data:** Techniques like caching filtered data and storing it as a parameter can significantly improve efficiency by minimizing redundant computations.

- **Flexibility with Panel:** Panel provides flexibility in designing interactive web apps, allowing developers to integrate various visualization components seamlessly.

By applying these concepts and techniques, developers can create efficient and responsive filtering applications using Panel, tailored to specific data exploration needs.
