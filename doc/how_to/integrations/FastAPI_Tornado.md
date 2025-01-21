# Embedding a Panel Server in FastAPI

Panel generally runs on the Bokeh server which itself runs on Tornado. However, it is also often useful to embed a Panel app in large web application, such as a FastAPI web server. [FastAPI](https://fastapi.tiangolo.com/) is especially useful compared to others like Flask and Django because of it's lightning fast, lightweight framework.

Following FastAPI's [Tutorial - User Guide](https://fastapi.tiangolo.com/tutorial/) make sure you first have FastAPI installed using: `conda install -c conda-forge fastapi`. Also make sure Panel is installed `conda install -c conda-forge panel`.

:::{admonition} warn
Embedding Panel in a FastAPI server has many drawbacks and shortcomings. We now strongly recommend running Panel directly on a FastAPI server as described in the [FastAPI how-to guide](FastAPI).
:::

## Configuration

Before we start adding a bokeh app to our FastAPI server we have to set up some of the basic plumbing. In the `examples/apps/fastApi` folder we will add some basic configurations.

You'll need to create a file called `examples/apps/fastApi/main.py`.

In `main.py` you'll need to import the following( which should all be already available from the above conda installs):

```python
import panel as pn
from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
```

Each of these will be explained as we add them in.

Next we are going to need to create an instance of FastAPI below your imports in `main.py` and set up the path to your templates like so:

```python
app = FastAPI()
templates = Jinja2Templates(directory="examples/apps/fastApi/templates")
```

We will now need to create our first route via an async function and point it to the path of our server:

```python
@app.get("/")
async def bkapp_page(request: Request):
    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("base.html", {"request": request, "script": script})
```

As you can see in this code we will also need to create an html  [Jinja2](https://fastapi.tiangolo.com/advanced/templates/#using-jinja2templates) template. Create a new directory named `examples/apps/fastApi/templates` and create the file `examples/apps/fastApi/templates/base.html` in that directory.

Now add the following to `base.html`. This is a minimal version but feel free to add whatever else you need to it.

```html
<!DOCTYPE html>
<html>
    <head>
        <title>Panel in FastAPI: sliders</title>
    </head>
    <body>
        {{ script|safe }}
    </body>
</html>
```

Return back to your `examples/apps/fastApi/main.py` file. We will use pn.serve() to start the bokeh server (Which Panel is built on). Configure it to whatever port and address you want, for our example we will use port 5000 and address 127.0.0.1. show=False will make it so the bokeh server is spun up but not shown yet. The allow_websocket_origin will list of hosts that can connect to the websocket, for us this is FastAPI so we will use (127.0.0.1:8000). The `createApp` function call in this example is how we call our panel app. This is not set up yet but will be in the next section.

```python
pn.serve({'/app': createApp},
        port=5000, allow_websocket_origin=["127.0.0.1:8000"],
        address="127.0.0.1", show=False)
```

You could optionally add BOKEH_ALLOW_WS_ORIGIN=127.0.0.1:8000 as an environment variable instead of setting it here. In conda it is done like this.

`conda env config vars set BOKEH_ALLOW_WS_ORIGIN=127.0.0.1:8000`

## Sliders app

Based on a standard FastAPI app template, this app shows how to integrate Panel and FastAPI.

The sliders app is in `examples/apps/fastApi/sliders`. We will cover the following additions/modifications to the Django2 app template:

  * `sliders/sinewave.py`: a parameterized object (representing your pre-existing code)

  * `sliders/pn_app.py`: creates an app function from the SineWave class

  To start with, in `sliders/sinewave.py` we create a parameterized object to serve as a placeholder for your own, existing code:

```python
import numpy as np
import param
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure


class SineWave(param.Parameterized):
    offset = param.Number(default=0.0, bounds=(-5.0, 5.0))
    amplitude = param.Number(default=1.0, bounds=(-5.0, 5.0))
    phase = param.Number(default=0.0, bounds=(0.0, 2 * np.pi))
    frequency = param.Number(default=1.0, bounds=(0.1, 5.1))
    N = param.Integer(default=200, bounds=(0, None))
    x_range = param.Range(default=(0, 4 * np.pi), bounds=(0, 4 * np.pi))
    y_range = param.Range(default=(-2.5, 2.5), bounds=(-10, 10))

    def __init__(self, **params):
        super(SineWave, self).__init__(**params)
        x, y = self.sine()
        self.cds = ColumnDataSource(data=dict(x=x, y=y))
        self.plot = figure(plot_height=400, plot_width=400,
                           tools="crosshair, pan, reset, save, wheel_zoom",
                           x_range=self.x_range, y_range=self.y_range)
        self.plot.line('x', 'y', source=self.cds, line_width=3, line_alpha=0.6)

    @param.depends('N', 'frequency', 'amplitude', 'offset', 'phase', 'x_range', 'y_range', watch=True)
    def update_plot(self):
        x, y = self.sine()
        self.cds.data = dict(x=x, y=y)
        self.plot.x_range.start, self.plot.x_range.end = self.x_range
        self.plot.y_range.start, self.plot.y_range.end = self.y_range

    def sine(self):
        x = np.linspace(0, 4 * np.pi, self.N)
        y = self.amplitude * np.sin(self.frequency * x + self.phase) + self.offset
        return x, y
```

However the app itself is defined we need to configure an entry point, which is a function that adds the application to it. In case of the slider app it looks like this in `sliders/pn_app.py`:

```python
import panel as pn

from .sinewave import SineWave

def createApp():
    sw = SineWave()
    return pn.Row(sw.param, sw.plot).servable()
```

We now need to return to our `main.py` and import the createApp function. Add the following import near the other imports:

```python
from sliders.pn_app import createApp
```

Your file structure should now be like the following:

```
fastApi
│   main.py
│
└───sliders
│   │   sinewave.py
│   │   pn_app.py
│
└───templates
    │   base.html
```

And your finished `main.py` should look like this:

```python
import panel as pn
from bokeh.embed import server_document
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from sliders.pn_app import createApp

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def bkapp_page(request: Request):
    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("base.html", {"request": request, "script": script})


pn.serve({'/app': createApp},
        port=5000, allow_websocket_origin=["127.0.0.1:8000"],
         address="127.0.0.1", show=False)
```

```
uvicorn main:app --reload
```

The output should give you a link to go to to view your app:

```
Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Go to that address and your app should be there running!

## Multiple apps


This is the most basic configuration for a bokeh server. It is of course possible to add multiple apps in the same way and then registering them with FastAPI in the way described in the [configuration](#configuration) section above. To see a multi-app FastAPI server have a look at ``examples/apps/fastApi_multi_apps`` and launch it with `uvicorn main:app --reload` as before.

To run multiple apps you will need to do the following:
1. Create a new directory in your and a new file with your panel app (ex. `sinewave.py`).
2. Create another pn_app file in your new directory (ex. `pn_app.py`) That might look something like this:
```
import panel as pn

from .sinewave import SineWave

def createApp2():
    sw = SineWave()
    return pn.Row(sw.param, sw.plot).servable()
```

With this as your new file structure:

```
fastApi
│   main.py
│
└───sliders
│   │   sinewave.py
│   │   pn_app.py
│   │
└───sliders2
│   │   sinewave.py
│   │   pn_app.py
│
└───templates
    │   base.html
```

3. Create a new html template (ex. app2.html) with the same contents as base.html in `examples/apps/fastApi/templates`
4. Import your new app in main.py `from sliders2.pn_app import createApp2`
5. Add your new app to the dictionary in pn.serve()

```python
{'/app': createApp, '/app2': createApp2}
```

7. Add a new async function to rout your new app (The bottom of `main.py` should look something like this now):

```python
@app.get("/")
async def bkapp_page(request: Request):
    script = server_document('http://127.0.0.1:5000/app')
    return templates.TemplateResponse("base.html", {"request": request, "script": script})

@app.get("/app2")
async def bkapp_page2(request: Request):
    script = server_document('http://127.0.0.1:5000/app2')
    return templates.TemplateResponse("app2.html", {"request": request, "script": script})

pn.serve({'/app': createApp, '/app2': createApp2},
        port=5000, allow_websocket_origin=["127.0.0.1:8000"],
         address="127.0.0.1", show=False)
```

With this as your file structure

```
fastApi
│   main.py
│
└───sliders
│   │   sinewave.py
│   │   pn_app.py
│   │
└───sliders2
│   │   sinewave.py
│   │   pn_app.py
│
└───templates
    │   base.html
    │   app2.html
```

Sliders 2 will be available at `http://127.0.0.1:8000/app2`

## Conclusion

That's it! You now have embedded panel in FastAPI! You can now build off of this to create your own web app tailored to your needs.
