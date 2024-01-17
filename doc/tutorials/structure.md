# Structuring Applications

:::{note} Tutorial 6. **Structuring Applications**
:icon: false

#### Classes and Design Patterns

Once you go beyond a simple dashboard or data app to a full fleshed application organizing your code and reasoning about state become a lot more difficult. In this section we will explore some common design patterns for structuring the code for your larger application.

:::

```{pyodide}
import param
import pandas as pd
import panel as pn

pn.extension('tabulator', 'vega', throttled=True)
```

## Building the app

Now that we have covered the preliminaries lets actually build an app that more closely resembles something you might actually use in production.

When building a more complex application we generally recommend using a class based construction and following best practices for object-oriented programming, specifically composition.

One particular design pattern that has proven quite successful across a wide range of use cases is something we will put into effect here, specifically we will construct:

- A `DataStore` that loads data from the catalog and defines a variable number of filters.
- A `View` component that consumes the data and then displays it.

#### The DataStore

We won't worry too much about the implementation details of this data store implementation but it's worth noting at a high-level it does a few simple things:

1. Initialize a data catalog using the automatic access controls.
2. Load a `table` from the data store and automatically generating a set of filters for each source.

```{pyodide}
from panel.viewable import Viewer

CARD_STYLE = """
:host {{
  box-shadow: rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px;
  padding: {padding};
}} """

class DataStore(Viewer):

    data = param.DataFrame()

    filters = param.List(constant=True)

    def __init__(self, **params):
        super().__init__(**params)
        dfx = self.param.data.rx()
        widgets = []
        for filt in self.filters:
            dtype = self.data.dtypes[filt]
            if dtype.kind == 'f':
                widget = pn.widgets.RangeSlider(name=filt, start=dfx[filt].min(), end=dfx[filt].max())
                condition = dfx[filt].between(*widget.rx())
            else:
                options = dfx[filt].unique().tolist()
                widget = pn.widgets.MultiChoice(name=filt, options=options)
                condition = dfx[filt].isin(widget.rx().rx.where(widget, options))
            dfx = dfx[condition]
            widgets.append(widget)
        self.filtered = dfx
        self.count = dfx.rx.len()
        self.total_capacity = dfx.t_cap.sum()
        self.avg_capacity = dfx.t_cap.mean()
        self.avg_rotor_diameter = dfx.t_rd.mean()
        self.top_manufacturers = dfx.groupby('t_manu').p_cap.sum().sort_values().iloc[-10:].index.to_list()
        self._widgets = widgets

    def filter(self, ):
        return

    def __panel__(self):
        return pn.Column('## Filters', *self._widgets, stylesheets=[CARD_STYLE.format(padding='5px 10px')], margin=10)

```

Here we declared a `DataStore` class that will be responsible for loading some data and transforming it in various ways and a `View` class that holds a reference to the `DataStore` as a parameter. Now we can have any number of concrete `View` classes that consume data from the DataStore and render it in any number of ways:

### The Views

```{pyodide}
import altair as alt
import holoviews as hv
import hvplot.pandas

class View(Viewer):

    data_store = param.ClassSelector(class_=DataStore)

class Table(View):

    columns = param.List(default=['p_name', 'p_year', 't_state', 't_county', 't_manu', 't_cap', 'p_cap'])

    def __panel__(self):
        data = self.data_store.filtered[self.param.columns]
        return pn.widgets.Tabulator(
            data, pagination='remote', page_size=13, stylesheets=[CARD_STYLE.format(padding='10px')],
            margin=10,
        )

class Histogram(View):

    def __panel__(self):
        df = self.data_store.filtered
        df = df[df.t_manu.isin(self.data_store.top_manufacturers)]
        fig = pn.rx(alt.Chart)((df.rx.len()>5000).rx.where(df.sample(5000), df),  title='Capacity by Manufacturer').mark_circle(size=8).encode(
            y="t_manu:N",
            x="p_cap:Q",
            yOffset="jitter:Q",
            color=alt.Color('t_manu:N').legend(None)
        ).transform_calculate(
            jitter="sqrt(-2*log(random()))*cos(2*PI*random())"
        ).properties(
            height=400,
            width=600,
        )
        return pn.pane.Vega(fig, stylesheets=[CARD_STYLE.format(padding='0')], margin=10)

class Indicators(View):

    def __panel__(self):
        style = {'stylesheets': [CARD_STYLE.format(padding='10px')]}
        return pn.FlexBox(
            pn.indicators.Number(
                value=self.data_store.total_capacity / 1e6, name='Total Capacity (TW)', format='{value:,.2f}', **style
            ),
            pn.indicators.Number(
                value=self.data_store.count, name='Count', format='{value:,.0f}', **style
            ),
            pn.indicators.Number(
                value=self.data_store.avg_capacity , name='Avg. Capacity (kW)', format='{value:,.2f}', **style
            ),
            pn.indicators.Number(
                value=self.data_store.avg_rotor_diameter, name='Avg. Rotor Diameter (m)', format='{value:,.2f}', **style
            ),
            pn.indicators.Number(
                value=self.data_store.avg_rotor_diameter, name='Avg. Rotor Diameter (m)', format='{value:,.2f}', **style
            ),
        )
```

The beauty of this compositional approach to constructing application components is that they are now usable in multiple contexts, e.g. you can use them in a notebook:

```{pyodide}
data_url = 'https://datasets.holoviz.org/windturbines/v1/windturbines.parq'

turbines = pd.read_parquet(data_url)

ds = DataStore(data=turbines, filters=['p_year', 'p_cap', 't_manu'])

pn.Row(
    ds,
    pn.Tabs(
        ('Table', Table(data_store=ds)),
        ('Histogram', Histogram(data_store=ds)),
        ('Indicators', Indicators(data_store=ds)),
        sizing_mode='stretch_width',
    )
)
```

Or we can coordinate these components inside of `App` class that handles the creation of the `View` components and lays them out on the pag or template:

```{pyodide}
class App(Viewer):

    data_store = param.ClassSelector(class_=DataStore)

    title = param.String()

    views = param.List()

    def __init__(self, **params):
        super().__init__(**params)
        updating = self.data_store.filtered.rx.updating()
        updating.rx.watch(lambda updating: pn.state.curdoc.hold() if updating else pn.state.curdoc.unhold())
        self._views = pn.FlexBox(*(view(data_store=self.data_store) for view in self.views), loading=updating)
        self._template = pn.template.MaterialTemplate(title=self.title)
        self._template.sidebar.append(self.data_store)
        self._template.main.append(self._views)

    def servable(self):
        if pn.state.served:
            return self._template.servable()
        return self

    def __panel__(self):
        return pn.Row(self.data_store, self._views)
```

Now let's see what we have built:

```{pyodide}
ds = DataStore(data=turbines, filters=['p_year', 'p_cap', 't_manu'])

app = App(data_store=ds, views=[Indicators, Histogram, Table], title='Windturbine Explorer')

app.servable()
```

<div class="header-box" style="box-shadow: rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px; padding: 5px 10px; border-left: 4px solid green;">

### Exercise

Now it is time to get started for real and extend the existing application. Build your own `View` and add it to the `App`, then deploy it.

</div>
