# Serve a REST API alongside your app

In addition to the interactive app itself, `panel serve` can publish a live REST API next to it, so scripts, dashboards, or monitoring tools can query the state of your app programmatically. REST support is provided by _REST providers_, selected with the `--rest-provider` commandline option:

```bash
panel serve app.py --rest-provider param
```

Panel ships with two providers, and additional providers can be registered through the `panel.io.rest` entry point.

## The Param provider

The Param provider publishes the parameters of any `param.Parameterized` object as a JSON endpoint. Use `pn.state.publish` to declare what to expose:

```python
import panel as pn

slider = pn.widgets.FloatSlider(name='Frequency', start=0, end=10)

pn.state.publish('slider', slider, ['value'])

slider.servable()
```

Serve it with `panel serve app.py --rest-provider param` and visit `http://localhost:5006/rest/slider` to get the current value back as JSON:

```bash
>>> curl http://localhost:5006/rest/slider
{"value": 0}
```

This works for any `Parameterized` object, not just widgets, as long as param can serialize the parameters.

::::{note}
Query parameters matching published parameter names are applied to the published object before the response is generated, so a published endpoint is not strictly read-only. Unknown query parameters are rejected with a 400 error. Only publish parameters you are comfortable exposing for remote update.
::::

### Exposing a dataframe

A common pattern is to let widgets drive a dataframe, show it in a table, and expose the dataframe itself at the REST endpoint. DataFrames are served as a list of records:

```python
import pandas as pd
import panel as pn
import param


class DataModel(param.Parameterized):

    n_points = param.Integer(default=10, bounds=(1, 100))

    multiplier = param.Number(default=1.0, bounds=(0.1, 10.0))

    data = param.DataFrame(default=pd.DataFrame({'x': [], 'y': []}))


model = DataModel()


def refresh(event=None):
    n, m = model.n_points, model.multiplier
    model.data = pd.DataFrame({
        'x': list(range(n)),
        'y': [round(i * m, 2) for i in range(n)],
    })


model.param.watch(refresh, ['n_points', 'multiplier'])
refresh()

pn.state.publish('data', model, ['data'])

pn.Column(
    '## Data explorer',
    model.param.n_points,
    model.param.multiplier,
    pn.widgets.Tabulator(model.param.data, height=300),
).servable()
```

Moving the sliders updates the table, and `http://localhost:5006/rest/data` always returns the current dataframe:

```bash
>>> curl http://localhost:5006/rest/data
{"data": [{"x": 0, "y": 0.0}, {"x": 1, "y": 1.0}, {"x": 2, "y": 2.0}, ...]}
```

::::{note}
Endpoints are shared across sessions: when a second session publishes an endpoint that is already published, its parameter values are synced to the existing values instead of getting a per-session endpoint. Publishing the same endpoint with a different set of parameters raises a `ValueError`.
::::

### Configuring the endpoint

By default the API is served under `/rest`. Use `--rest-endpoint` to change it:

```bash
panel serve app.py --rest-provider param --rest-endpoint api
```

Requests to an unpublished path return an empty response.

Note that the provider executes your app script at server startup to collect the published endpoints, so any module-level side effects in the script run again at startup.

## The Tranquilizer provider

While the Param provider publishes parameter values, the Tranquilizer provider publishes functions that compute a result before returning it. Decorate functions with `@tranquilize` and serve with `--rest-provider tranquilizer`:

```python
import panel as pn

from tranquilizer import tranquilize

select = pn.widgets.Select(
    name='Cheese', options=['Cheddar', 'Mozarella', 'Parmeggiano'], value='Cheddar'
)


def update_cache(event):
    pn.state.cache['cheese'] = event.new


select.param.watch(update_cache, 'value')
pn.state.cache['cheese'] = 'Cheddar'


@tranquilize()
def order(cheese: str = 'Cheddar'):
    """Order some cheese."""
    return f"I'm afraid we're fresh out of {cheese.lower()}, sir."


select.servable()
```

Each tranquilized function is served at `/rest/<function name>`, and its arguments are passed as query parameters:

```bash
>>> curl "http://localhost:5006/rest/order?cheese=Gouda"
"I'm afraid we're fresh out of gouda, sir."
```

This requires the [`tranquilizer`](https://github.com/QuantStack/tranquilizer) package to be installed. Tranquilizer generates Swagger/OpenAPI documentation for the functions, but those pages are not reachable when the API is served through Panel, so document your functions and their arguments yourself.

## Session info

Passing `--rest-session-info` additionally serves information about the server's session history at `/rest/session_info`, independent of the configured `--rest-provider` and `--rest-endpoint`.

## Writing a custom provider

A REST provider is a function that takes the list of served files and the endpoint name and returns Tornado routing patterns:

```python
def my_rest_provider(files, endpoint):
    ...
    return [(rf"^/{endpoint}/.*", MyHandler, {})]
```

Register it under the `panel.io.rest` entry point in your package metadata, after which it can be selected with `panel serve app.py --rest-provider <name>`.
