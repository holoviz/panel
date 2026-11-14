# Serve a REST API

A Panel server can expose HTTP endpoints next to an application. Declare them in a plugin and pass the module to `panel serve --plugins`. [Add custom endpoints](endpoints) covers the Tornado and FastAPI forms of a plugin. This page uses the FastAPI form, because `--server fastapi` publishes the routes in an OpenAPI schema.

```bash
pip install fastapi uvicorn
```

`--rest-provider` and `pn.state.publish`, added in Panel 0.10, still serve a Param provider and a Tranquilizer provider. Both are deprecated and will be removed in Panel 2.0, and both run only on the Tornado server. The plugin below is the supported way to serve the dataframe for one session, to accept an argument, and to read the OpenAPI documentation.

## Serve one session's dataframe

The application keeps a slider-driven dataframe in a table. The endpoint returns that dataframe for the session that produced it, so two open sessions each read their own rows.

The dataframe has to live in a module that both the application and the plugin import. `panel serve` executes the application script once per session, in a new namespace, while the plugin is imported once into the process. A dict created in the script would be a different object in every session and invisible to the plugin.

```python
# shared.py
frames = {}
```

```python
# app.py
import pandas as pd
import panel as pn
import param

from shared import frames

class Controls(param.Parameterized):
    rows = param.Integer(default=5, bounds=(1, 20))
    scale = param.Number(default=1.0, bounds=(0.1, 5.0))

controls = Controls()

# Drop the session's data once it ends so the server does not keep it forever
pn.state.on_session_destroyed(lambda ctx: frames.pop(ctx.id, None))

def table(rows, scale):
    session_id = pn.state.curdoc.session_context.id
    df = pd.DataFrame({
        'x': list(range(rows)),
        'y': [round(i * scale, 3) for i in range(rows)],
    })
    frames[session_id] = df
    return pn.Column(
        pn.pane.Markdown(f'Session `{session_id}` is served at `/rest/data/{session_id}`.'),
        pn.widgets.Tabulator(df, disabled=True, sizing_mode='stretch_width'),
    )

pn.Column(
    pn.widgets.IntSlider.from_param(controls.param.rows, name='Rows'),
    pn.widgets.FloatSlider.from_param(controls.param.scale, name='Scale'),
    pn.bind(table, controls.param.rows, controls.param.scale),
).servable()
```

`table` runs in the session, so `pn.state.curdoc.session_context.id` is that session's id. Moving a slider runs `table` again and replaces the dataframe stored under the same id.

```python
# plugin.py
from fastapi import APIRouter, HTTPException

from shared import frames

ROUTER = APIRouter(prefix='/rest')

@ROUTER.get('/data/{session_id}')
def session_data(session_id: str):
    """Records for one Panel session."""
    df = frames.get(session_id)
    if df is None:
        raise HTTPException(status_code=404, detail=f'No data for session {session_id!r}.')
    return df.to_dict(orient='records')

@ROUTER.get('/order')
def order(cheese: str):
    """I'd like to buy some cheese!"""
    return f"I'm afraid we're fresh out of {cheese.lower()}, sir."
```

From the directory that contains these three modules:

```bash
panel serve app.py --server fastapi --plugins plugin
```

The page shows the session id. Substitute that id into the request. With the sliders left at their defaults the endpoint returns five records:

```bash
>>> curl http://localhost:5006/rest/data/<session id>
[{"x":0,"y":0.0},{"x":1,"y":1.0},{"x":2,"y":2.0},{"x":3,"y":3.0},{"x":4,"y":4.0}]
```

An id the server has not created returns HTTP 404:

```bash
>>> curl http://localhost:5006/rest/data/nope
{"detail":"No data for session 'nope'."}
```

A second visit, for example a private window, gets a new session id and a new entry in `frames`. The first session's endpoint still returns the first session's rows until that session is destroyed, at which point its entry is removed.

## Arguments and OpenAPI docs

The `order` route on the same router takes `cheese` as a query parameter. FastAPI reads the annotation and the docstring into the schema, and rejects a request that omits the parameter with HTTP 422.

```bash
>>> curl "http://localhost:5006/rest/order?cheese=Gouda"
"I'm afraid we're fresh out of gouda, sir."
```

The interactive documentation is the FastAPI page at <http://localhost:5006/docs>. The schema is at <http://localhost:5006/openapi.json> and lists `/rest/data/{session_id}` and `/rest/order`.

`--server asgi` has no plugin routers. A Tornado plugin declares `ROUTES` instead of `ROUTER` and has no OpenAPI page; the [endpoints guide](endpoints) shows that form.

## Deprecated providers

:::{admonition} Deprecated
:class: warning

`--rest-provider`, `--rest-endpoint`, `pn.state.publish` and the `panel.io.rest` entry point will be removed in Panel 2.0. `--server fastapi` and `--server asgi` exit with an error if `--rest-provider` is set. The replacement is a plugin, as in the sections above and in the [upgrade guide](../../upgrade).
:::

### Param provider

`pn.state.publish` registers parameters on a `Parameterized`, and `--rest-provider param` serves each registration as JSON under the REST prefix. Pass the parameter names. The default is every parameter, including the constant `name`, and the next session then fails while the script is loading with `Constant parameter 'name' cannot be modified`.

```python
import panel as pn
import param

class Slider(param.Parameterized):
    value = param.Integer(default=0, bounds=(0, 100))

slider = Slider()
pn.state.publish('slider', slider, ['value'])
pn.widgets.IntSlider.from_param(slider.param.value).servable()
```

```bash
panel serve app.py --rest-provider param
```

The provider also executes the script once while the server starts, and the handler answers from that first object:

```bash
>>> curl http://localhost:5006/rest/slider
{"value": 0}
```

`publish` copies that object's values onto each later session and watches the named parameters. The handler keeps reading the first object. A second session's edit does not update it, so the endpoint is a single shared value and stays on the value written by the first session. `--rest-endpoint api` changes the prefix, so the same object is served at `/api/slider`.

A query string is parsed into lists of strings. Param deserializes a JSON string, and the request fails with HTTP 500:

```bash
>>> curl "http://localhost:5006/rest/slider?value=4"
{"error": {"code": 500, "message": "Internal Server Error"}}
```

A `param.DataFrame` on that same object is serialized as a list of records, such as `[{"x": 0}, {"x": 1}, {"x": 2}]`.

### Tranquilizer provider

`--rest-provider tranquilizer` imports [Tranquilizer](https://github.com/ContinuumIO/tranquilizer), finds every function decorated with `@tranquilize` in the files passed to `panel serve`, and mounts the Flask application it builds. Arguments become query parameters. With the defaults, an argument without an annotation is a string.

```python
from tranquilizer import tranquilize

@tranquilize()
def order(cheese):
    """I'd like to buy some cheese!"""
    return f"I'm afraid we're fresh out of {cheese.lower()}, sir."
```

```bash
panel serve cheese.py --rest-provider tranquilizer
```

```bash
>>> curl "http://localhost:5006/rest/order?cheese=Gouda"
"I'm afraid we're fresh out of gouda, sir."
```

Tranquilizer 0.9.2 requires `werkzeug<2.1`. Current Flask releases require a newer Werkzeug, so this provider cannot be installed into an environment that already depends on a current Flask.

Tranquilizer generates a Swagger UI and a `/swagger.json` spec. Panel forwards only paths under the REST prefix to that application, and the UI is registered at `/` and the spec at `/swagger.json`. `/` is the Panel index, `/swagger.json` is not forwarded, and `/rest/` and `/rest/swagger.json` are not documentation routes, so the UI is not available on a Panel server. The FastAPI `order` route above takes the same argument and is documented at `/docs`.

A third-party provider can still be registered with the `panel.io.rest` entry point, described under [Rest plugins](../../developer_guide/extensions.md#rest-plugins). That entry point will be removed with the rest of this API.

## Session information

`--rest-session-info` is unrelated to `--rest-provider`. It serves `pn.state.session_info` as JSON at `/session_info` on every server implementation. See [Serving session information](endpoints.md#serving-session-information).
