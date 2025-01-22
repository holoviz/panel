# Running Panel apps in FastAPI

Panel generally runs on the Bokeh server, which itself runs on [Tornado](https://tornadoweb.org/en/stable/). However, it is also often useful to embed a Panel app in an existing web application, such as a [FastAPI](https://fastapi.tiangolo.com/) web server.

Since Panel 1.5.0 it is possible to run Panel application(s) natively on a FastAPI based server. Therefore this how-to guide will explain how to add Panel application(s) directly to an existing FastAPI application. This functionality is new and experimental so we also provide the original [how-to guide to embed a Tornado based Panel server application inside a FastAPI application](./FastAPI_Tornado).

By the end of this guide, you'll be able to run a FastAPI application that serves a simple interactive Panel app. The Panel app will consist of a slider widget that dynamically updates a string of stars (⭐) based on the slider's value.

## Setup

Following FastAPI's [Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/) make sure you first have [FastAPI](https://fastapi.tiangolo.com/) and [bokeh-fastapi] installed using:

::::{tab-set}

:::{tab-item} `pip`
```bash
pip install panel[fastapi]
```
:::

:::{tab-item} `conda`
```bash
conda install -c conda-forge bokeh-fastapi
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

from panel.io.fastapi import add_panel_app

@add_panel_app('/panel', app=app, title='My Panel App')
def create_panel_app():
    slider = pn.widgets.IntSlider(name='Slider', start=0, end=10, value=3)
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
    slider = pn.widgets.IntSlider(name='Slider', start=0, end=10, value=3)
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

If you visit `http://127.0.0.1:8000` you will see the Panel application.

## Adding multiple applications

The `add_application` decorator is useful when server an application defined in a function, if you want to serve multiple applications, whether they are existing Panel objects, functions, or paths to Panel application scripts you can use the `add_applications` function instead, e.g.:

```python
import panel as pn

from fastapi import FastAPI
from panel.io.fastapi import add_applications

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

def create_panel_app():
    slider = pn.widgets.IntSlider(name='Slider', start=0, end=10, value=3)
    return slider.rx() * '⭐'

add_applications({
    "/panel_app1": create_panel_app,
    "/panel_app2": pn.Column('I am a Panel object!'),
    "/panel_app3": "my_panel_app.py"
}, app=app)
```

## Tips & Tricks

### Running Behind a Proxy

In some cases, you might be running your FastAPI app behind a reverse proxy, which adds an extra path prefix that your application doesn't directly handle. This is common when working in environments like JupyterHub or deploying to Kubernetes.

For instance, if your FastAPI `/` endpoint is accessed at `https://some.domain/some/path/`, you will need to specify the path prefix when starting your FastAPI server. To do this, use the flag `--root-path /some/path/`. This ensures you can access the OpenAPI docs at `https://some.domain/some/path/docs`.

For more details, refer to the [Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/) guide.

## Conclusion

That's it! You now have embedded panel in FastAPI! You can now build off of this to create your own web app tailored to your needs.
