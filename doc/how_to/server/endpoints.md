# Add custom endpoints to the Panel Server

The default Panel server is built on top of Tornado, which is a general framework for building performant web applications. This means it is very straightforward to add custom endpoints to serve as API endpoints for the application or to perform anything else we might want to do.

Endpoints are added with a so called plugin, a module that declares the routes to serve alongside the applications and that is passed to `panel serve` with the `--plugins` argument. How the routes are declared depends on the server implementation:

- `--server tornado` (the default): a `ROUTES` variable holding [Tornado `RequestHandler`](https://www.tornadoweb.org/en/stable/web.html) classes.
- `--server fastapi`: a `ROUTER` variable holding a [FastAPI `APIRouter`](https://fastapi.tiangolo.com/reference/apirouter/).
- `--server asgi`: not supported, use `--server fastapi` to declare custom endpoints on an ASGI server.

A plugin module may declare both, in which case it can be served on either implementation.

## Declaring a Tornado endpoint

To add a new endpoint to our server we have to implement a so called [Tornado `RequestHandler`](https://www.tornadoweb.org/en/stable/web.html). A `RequestHandler` implements has to implement one or more methods corresponding to a so called HTTP verb method. The most common of these are:

- `.get`: Handles HTTP GET requests
- `.post`: Handles HTTP POST requests
- `.head`: Handles HTTP HEAD requests

As a very simple example we might implement a GET request that sums up numbers:

```python
from tornado.web import RequestHandler, HTTPError

class SumHandler(RequestHandler):

    def get(self):
        values = [self.get_argument(arg) for arg in self.request.arguments]
        if not all(arg.isdigit() for arg in values):
            raise HTTPError(400, 'Arguments were not all numbers.')
        self.set_header('Content-Type', 'text/plain')
        self.write(str(sum([int(v) for v in values])))

ROUTES = [('/sum', SumHandler, {})]
```

This `RequestHandler` does a few things:

1. Get the values of all request arguments
2. Validate the input by check if they are all numeric digits
3. Set the `Content-Type` header to declare we are returning text
4. Sum the values and return the `write` the result as a string

Lastly, a valid Panel server plugin must also declares the `ROUTES` to add to the server. In this case we will declare that our handler should be served on the route `/sum`.

Now let's try this handler, write it to a local file called `plugin.py` and then run:

```bash
panel serve --plugins plugin
```

A Panel server will start serving our new endpoint, which means we can visit `http://localhost:5006/sum` which should display zero.

If we add some request arguments we can actually see it summing our data:

```bash
>>> curl http://localhost:5006/sum?a=1&b=3&c=39
42
```

## Declaring a FastAPI endpoint

When serving with `--server fastapi` the endpoints are declared as FastAPI routes instead. Since the FastAPI application itself is created by `panel serve`, the plugin declares an [`APIRouter`](https://fastapi.tiangolo.com/reference/apirouter/), which is FastAPI's way of collecting routes that are registered on an application later:

```python
from fastapi import APIRouter, HTTPException

ROUTER = APIRouter()

@ROUTER.get('/sum')
def sum_values(a: int = 0, b: int = 0):
    if a < 0 or b < 0:
        raise HTTPException(400, 'Arguments must be positive.')
    return a + b
```

Write this to a local file called `plugin.py` and serve it with:

```bash
panel serve --server fastapi --plugins plugin
```

```bash
>>> curl "http://localhost:5006/sum?a=3&b=39"
42
```

`ROUTER` may also be a list of routers, e.g. if you want to group the endpoints by concern or apply a different prefix or set of dependencies to each of them.

Everything an `APIRouter` supports is available here, including websocket routes, dependencies, background tasks and Pydantic request and response models. Panel keeps ownership of the paths it serves, i.e. the application routes, `/static/*` and the authentication endpoints, so a plugin cannot shadow those. The index page and `/favicon.ico` on the other hand are served by Panel only as a convenience, so declaring them yourself takes precedence.

## Sharing state with the applications

The plugin is imported once into the same process that runs the applications, so an endpoint can read and modify state the applications display. Put the state in a module that both import; Python imports a module only once, so they share the same object:

```python
# shared.py
import param

class Settings(param.Parameterized):
    threshold = param.Number(default=0.5, bounds=(0, 1))

settings = Settings()
```

The application binds a widget to it, so every session shows and edits the same value:

```python
# app.py
import panel as pn

from shared import settings

pn.Column(
    pn.widgets.FloatSlider.from_param(settings.param.threshold),
    pn.bind(lambda t: f'Threshold: {t}', settings.param.threshold),
).servable()
```

The plugin exposes the same value over HTTP. Here it is declared for both server implementations:

```python
# plugin.py
import json

from fastapi import APIRouter, HTTPException
from tornado.web import HTTPError, RequestHandler

from shared import settings

def update(threshold):
    try:
        settings.threshold = threshold
    except ValueError as e:
        raise HTTPError(400, str(e)) from e

class SettingsHandler(RequestHandler):

    def get(self):
        self.write({'threshold': settings.threshold})

    def put(self):
        update(json.loads(self.request.body)['threshold'])
        self.write({'threshold': settings.threshold})

ROUTES = [('/api/settings', SettingsHandler, {})]

ROUTER = APIRouter(prefix='/api')

@ROUTER.get('/settings')
def get_settings():
    return {'threshold': settings.threshold}

@ROUTER.put('/settings')
def put_settings(threshold: float):
    try:
        settings.threshold = threshold
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return {'threshold': settings.threshold}
```

```bash
panel serve app.py --plugins plugin
curl -X PUT -d '{"threshold": 0.8}' http://localhost:5006/api/settings
```

Every open session updates to the new threshold. With `--server fastapi` the FastAPI route takes `threshold` as a query parameter, i.e. `curl -X PUT "http://localhost:5006/api/settings?threshold=0.8"`.

This replaces `pn.state.publish` and `--rest-provider`, which are deprecated and will be removed in Panel 2.0. Unlike those, the endpoint decides which parameters are exposed, which HTTP methods modify them and how the response looks.

Custom endpoints are not covered by Panel's authentication. On Tornado, subclass `bokeh.server.views.auth_request_handler.AuthRequestHandler` instead of `RequestHandler` and decorate the methods with `tornado.web.authenticated`, which rejects requests that Panel's configured authentication does not resolve to a user. On FastAPI, protect the routes with a [dependency](https://fastapi.tiangolo.com/tutorial/security/).

## Serving session information

Panel can also serve information about the sessions it has created, i.e. the contents of `pn.state.session_info`, as JSON on `/session_info`. Enable it with `--rest-session-info` and set `--session-history` to the number of sessions to keep:

```bash
panel serve app.py --rest-session-info --session-history 100
```

The Tornado server also serves this on `/rest/session_info`, nested under a `session_info` key. That route is deprecated and will be removed in Panel 2.0.

## Using `pn.serve`

When serving programmatically you can provide handlers explicitly using the `extra_patterns` argument, e.g. you can provide the `SumHandler` by running:

```python
import panel as pn

from plugin import SumHandler

pn.serve({}, extra_patterns=[('/sum', SumHandler)])
```

If you are not using `panel serve` and want to serve Panel applications alongside FastAPI routes, you do not need a plugin at all: declare the routes on your own FastAPI application and add the Panel applications to it as described in the [FastAPI](../integrations/FastAPI) guide. The same applies to Django views, see the [Django](../integrations/Django) guide.
