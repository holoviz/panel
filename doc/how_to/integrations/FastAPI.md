# Running Panel apps in FastAPI

Panel generally runs on the Bokeh server, which itself runs on [Tornado](https://tornadoweb.org/en/stable/). However, it is also often useful to embed a Panel app in an existing web application, such as a [FastAPI](https://fastapi.tiangolo.com/) web server.

Since Panel 1.5.0 it is possible to run Panel application(s) natively on a FastAPI based server. Therefore this how-to guide will explain how to add Panel application(s) directly to an existing FastAPI application. If you would rather embed a separate Tornado based Panel server inside your FastAPI application we also provide a [how-to guide for that](./FastAPI_Tornado).

By the end of this guide, you'll be able to run a FastAPI application that serves a simple interactive Panel app. The Panel app will consist of a slider widget that dynamically updates a string of stars (⭐) based on the slider's value.

## Setup

Following FastAPI's [Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/) make sure you first have [FastAPI](https://fastapi.tiangolo.com/) installed using:

::::{tab-set}

:::{tab-item} `pip`
```bash
pip install panel[fastapi]
```
:::

:::{tab-item} `conda`
```bash
conda install -c conda-forge fastapi uvicorn
```
:::

::::

## Create a FastAPI application

Start by creating a FastAPI application. In this application, we will define a root endpoint that returns a simple JSON response. Open your text editor or IDE and create a file named main.py:

```python
from fastapi import FastAPI

# Initialize FastAPI application
app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}
```

## Create a Panel Application

Next we will define a simple Panel application that allows you to control the number of displayed stars with an integer slider and decorate it with the `add_panel_app` decorator:

```python
import panel as pn

from panel.io.fastapi import add_application

@add_application('/panel', app=app, title='My Panel App')
def create_panel_app():
    slider = pn.widgets.IntSlider(label='Slider', start=0, end=10, value=3)
    return slider.rx() * '⭐'
```

That's it! This decorator will map a specific URL path to the Panel app, allowing it to be served as part of the FastAPI application.

The complete file should now look something like this:

```python
import panel as pn

from fastapi import FastAPI
from panel.io.fastapi import add_application

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@add_application('/panel', app=app, title='My Panel App')
def create_panel_app():
    slider = pn.widgets.IntSlider(label='Slider', start=0, end=10, value=3)
    return slider.rx() * '⭐'
```

Now run it with:

```bash
fastapi dev main.py
```

You should see the following output:

```bash
INFO     Using path main.py
INFO     Resolved absolute path /home/user/code/awesomeapp/main.py
INFO     Searching for package file structure from directories with __init__.py files
INFO     Importing from /home/user/code/awesomeapp/fast_api

 ╭─ Python module file ─╮
 │                      │
 │  🐍 main.py          │
 │                      │
 ╰──────────────────────╯

INFO     Importing module main
/panel
INFO     Found importable FastAPI app

 ╭─ Importable FastAPI app ─╮
 │                          │
 │  from main import app    │
 │                          │
 ╰──────────────────────────╯

INFO     Using import string main:app

 ╭────────── FastAPI CLI - Development mode ───────────╮
 │                                                     │
 │  Serving at: http://127.0.0.1:8000                  │
 │                                                     │
 │  API docs: http://127.0.0.1:8000/docs               │
 │                                                     │
 │  Running in development mode, for production use:   │
 │                                                     │
 │  fastapi run                                        │
 │                                                     │
 ╰─────────────────────────────────────────────────────╯

INFO:     Will watch for changes in these directories: ['/home/user/code/awesomeapp/']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [39089] using WatchFiles
INFO:     Started server process [39128]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

If you visit `http://127.0.0.1:8000/panel` you will see the Panel application.

## Adding multiple applications

The `add_application` decorator is useful when serving an application defined in a function, if you want to serve multiple applications, whether they are existing Panel objects, functions, or paths to Panel application scripts you can use the `add_applications` function instead, e.g.:

```python
import panel as pn

from fastapi import FastAPI
from panel.io.fastapi import add_applications

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

def create_panel_app():
    slider = pn.widgets.IntSlider(label='Slider', start=0, end=10, value=3)
    return slider.rx() * '⭐'

add_applications({
    "/panel_app1": create_panel_app,
    "/panel_app2": pn.Column('I am a Panel object!'),
    "/panel_app3": "my_panel_app.py"
}, app=app)
```

`add_applications` returns a handle exposing the `FastAPI` application as `.app`, the underlying ASGI application Panel uses to serve the apps as `.asgi` and the Bokeh server configuration as `.core`.

Panel installs itself as an ASGI middleware on the FastAPI application, which claims only the paths it owns and delegates everything else to FastAPI. This means it does not matter whether you declare your own FastAPI routes before or after calling `add_applications`, and you may call `add_applications` more than once on the same app.

## Supported endpoints

Alongside the application paths themselves the integration serves the same endpoints as `panel serve`:

- `/<app>/ws`: the websocket connection for a session.
- `/<app>/autoload.js`: the script for embedding an app in an external page.
- `/<app>/metadata`: the app metadata, if it declares any.
- `/static/extensions/...` and component resources, i.e. the JS and CSS of Panel and any extensions in use.
- `/favicon.ico`, overridable with the `ico_path` argument.
- The index page listing all applications, customizable with the `index` and `index_titles` arguments.

The `liveness` and `session_history` arguments add `/liveness` and `/session_info` endpoints respectively, and `static_dirs` mounts additional directories, just as the equivalent `panel serve` options do:

```python
add_applications(
    {"/panel_app": create_panel_app},
    app=app,
    liveness=True,
    session_history=10,
    static_dirs={'assets': './assets'},
)
```

## Wildcard routes

Applications can be served on [wildcard routes](../server/wildcard_routes) and the captured parameters are made available on `pn.state.route_params`:

```python
import panel as pn

from fastapi import FastAPI
from panel.io.fastapi import add_applications

app = FastAPI()

def greet():
    return pn.pane.Markdown(f"# Hello {pn.state.route_params['name']}!")

add_applications({"/user/{name}": greet}, app=app)
```

## Serving under a prefix

To serve all Panel applications below a common path pass a `prefix`:

```python
add_applications({"/panel_app": create_panel_app}, app=app, prefix='/apps')
```

The app is then served at `/apps/panel_app` and all resource and websocket URLs are prefixed accordingly. This is independent of the `--root-path` handled by the proxy, described below.

## Authentication

[Authentication](../authentication/index) is configured with the same arguments you would pass to `panel serve` or `pn.serve`, e.g. to require a password:

```python
add_applications(
    {"/panel_app": create_panel_app},
    app=app,
    basic_auth='my_password',
    cookie_secret='my_super_safe_cookie_secret',
)
```

or to authenticate against an OAuth provider:

```python
add_applications(
    {"/panel_app": create_panel_app},
    app=app,
    oauth_provider='azure',
    oauth_key='...',
    oauth_secret='...',
    oauth_encryption_key='...',
    cookie_secret='...',
)
```

Panel then serves the `/login` and `/logout` endpoints and authenticates the application routes, the websocket connection, the autoload and metadata endpoints and any `static_dirs`. Routes you declared on the FastAPI application itself are never touched, so securing your own API endpoints remains up to you.

Cookies are minted and validated identically on both servers, so a user logged in against a Tornado based `panel serve` process is accepted by a FastAPI process configured with the same `cookie_secret` (and `oauth_encryption_key`), and vice versa. That makes it possible to run both behind the same load balancer, or to migrate from one to the other without logging everyone out.

## Tips & Tricks

### Running Behind a Proxy

In some cases, you might be running your FastAPI app behind a reverse proxy, which adds an extra path prefix that your application doesn't directly handle. This is common when working in environments like JupyterHub or deploying to Kubernetes.

For instance, if your FastAPI `/` endpoint is accessed at `https://some.domain/some/path/`, you will need to specify the path prefix when starting your FastAPI server. To do this, use the flag `--root-path /some/path/`. This ensures you can access the OpenAPI docs at `https://some.domain/some/path/docs`.

For more details, refer to the [Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/) guide.

## Conclusion

That's it! You now have embedded panel in FastAPI! You can now build off of this to create your own web app tailored to your needs.

A complete example combining FastAPI routes, the `add_application` decorator, `add_applications` and a wildcard route can be found in `examples/apps/fastApi_native`, which you can launch with `uvicorn main:app --reload`.
