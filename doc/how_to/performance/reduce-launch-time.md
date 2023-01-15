# Reduce the launch time of your data app

In this *how to guide* we will provide tips and tricks for reducing the time it takes to launch your
app. This will improve the *user experience* and enable you to serve more users.

In this guide we will focus on how you can improve the architecture and code of
your app.

Below we will explain how to identify and remove bottlenecks. But first you will need to understand
what happens when your app is launched.

## Understanding the launch

- A user using a browser (client) **requests** the page
- The server **runs** the .py file of the page and **generates** a html document
- The server **responds** by sending the html document to the client
- The client **receives** the html document and **renders** it
- The client opens a **web socket connection** to the server
- Any **deferred components** are sent from the server to the client over the web socket
- The client receives the deferred components and **updates** the page

As you can see the bottlenecks can be in many places, and on both the server and client side.

## An example multi-page app

Lets create a multi-page application consisting of a `home.py` page and a `dashboard.py` page.

```python
# home.py
import panel as pn

SECTION1 = """
## Panel works with the tools you know and love

[Panel](https://panel.holoviz.org/) makes it easy to combine widgets, plots, tables and other viewable Python objects into custom analysis tools, applications, and dashboards.
"""

IMAGE1 = pn.pane.GIF("https://assets.holoviz.org/panel/readme/linked_brushing.gif", alt_text="Panel NYC Taxi app w. Linked Brushing", link_url="https://panel.holoviz.org/reference/templates/FastGridTemplate.html")

SECTION2 = """
Panel works really well with the visualization tools you already know and love like [Altair/ Vega](https://panel.holoviz.org/reference/panes/Vega.html), [Bokeh](https://panel.holoviz.org/reference/panes/Bokeh.html), [Datashader](https://datashader.org/), [Deck.gl/ pydeck](https://panel.holoviz.org/reference/panes/DeckGL.html), [Echarts/ pyecharts](https://panel.holoviz.org/reference/panes/ECharts.html), [Folium](https://panel.holoviz.org/reference/panes/Folium.html), [HoloViews](https://holoviews.org/), [hvPlot](https://hvplot.holoviz.org), [plotnine](https://panel.holoviz.org/reference/panes/Matplotlib.html), [Matplotlib](https://panel.holoviz.org/reference/panes/Matplotlib.html), [Plotly](https://panel.holoviz.org/reference/panes/Plotly.html), [PyVista/ VTK](https://panel.holoviz.org/reference/panes/VTK.html), [Seaborn](https://panel.holoviz.org/gallery/styles/SeabornStyle.html) and more. Panel also works with the [ipywidgets](https://panel.holoviz.org/reference/panes/IPyWidget.html) ecosystem.
"""

IMAGE2 = pn.pane.GIF("https://assets.holoviz.org/panel/readme/dataviz.gif", alt_text="Pythons DataViz works with Panel", link_url="https://panel.holoviz.org/reference/index.html#panes")

component = pn.Column(
    SECTION1, IMAGE1, SECTION2, IMAGE2
)

NAVIGATION = """
## Navigation

[home](/)
[dashboard](dashboard)
"""

pn.template.FastListTemplate(
    site="Panel", site_url="https:\\panel.holoviz.org",
    title="The most flexible data app framework for Python", main=[component], sidebar=[NAVIGATION]
).servable()
"""
```

```python
# dashboard.py
import numpy as np
import pandas as pd

from matplotlib.figure import Figure

import panel as pn

pn.extension(sizing_mode="stretch_width")

data_url = "https://cdn.jsdelivr.net/gh/holoviz/panel@master/examples/assets/occupancy.csv"
primary_color = "#0072B5"
secondary_color = "#94EA84"

data = pd.read_csv(data_url, parse_dates=["date"]).set_index("date")

def mpl_plot(avg, highlight):
    fig = Figure(figsize=(10, 5))
    ax = fig.add_subplot()
    avg.plot(ax=ax, c=primary_color)
    if len(highlight):
        highlight.plot(style="o", ax=ax, c=secondary_color)
    return fig

def find_outliers(variable="Temperature", window=20, sigma=10, view_fn=mpl_plot):
    avg = data[variable].rolling(window=window).mean()
    residual = data[variable] - avg
    std = residual.rolling(window=window).std()
    outliers = np.abs(residual) > std * sigma
    return view_fn(avg, avg[outliers])

variable = pn.widgets.RadioBoxGroup(
    name="Variable", value="Temperature", options=list(data.columns)
)

window = pn.widgets.IntSlider(name="Window", value=20, start=1, end=60)

# Reactive Functions
reactive_outliers = pn.bind(find_outliers, variable, window, 10)

panel = pn.panel(reactive_outliers, sizing_mode="scale_both")

pn.template.FastListTemplate(
    site="Panel",
    title="Dashboard",
    accent_base_color=primary_color,
    header_background=primary_color,
    sidebar=[variable, window],
    main = [reactive_outliers],
).servable()
```

Lets serve the apps with

```bash
panel serve home.py dashboard.py --index home
```

The will look like

![Home App](https://user-images.githubusercontent.com/42288570/212533365-ca493863-2a46-4107-beca-05d44830fa31.jpg)
![Dashboard App](https://user-images.githubusercontent.com/42288570/212533385-8350e3d3-a1b7-4aa6-a125-6f50f66f7422.jpg)

## Identify the bottlenecks

If you want to identify bottlenecks you can

- [] Use the developer tools in the browser to measure the time it takes to load your app in the client
- [] Use pytest-benchmark to measure the time it takes to process your code on the server
- [] Use the admin and a profiler to identify more bottlenecks on the server side
- [] Analyze your users and forecast how they will be interacting with your app
- [] Use Playwright with Loadwright to measure the launch time when multiple users interact with your app

### Use the developer tools in the browser

Please

- Open the *Dashboard* page at http://localhost:5006/dashboard
- Open the *Home* page at http://localhost:5006
- Open the developer tools and navigate to the *network* tab
- Hard refresh the page by holding the Ctrl key and clicking the Refresh button
- Sort the table by *Time* desc

On my laptop it looks like

![Home Developer Tools View](https://user-images.githubusercontent.com/42288570/212533878-c55ea350-da9a-4218-9a7f-10f7165ae481.jpg)

You see that the total time it takes for the user to launch the app is 1.75 seconds. Of which loading the DOM content takes 1.01 seconds.

The key bottlenecks are

- rendering the page: This is the 1.75 - 1.01 seconds it takes to render the document by the browser
- `localhost`: This is the time it takes to run `home.py` and generate the `.html` document by the Panel server
- `data:image...`: This is the time it take to load the `.gif` image
- `plotly-2.10.1-min.js`: This is the time it takes to load the Plotly `.js` library which is not even used on this page!
- `fast` assets: Lots of *fast* `.js` and `.css` files that seem not to be *minimized*.

If we do the same for the *Dashboard* page we see

![Dashboard Developer Tools](https://user-images.githubusercontent.com/42288570/212534451-f65be0cb-7c42-4416-96b7-052d07dc4858.jpg)

The key bottlenecks are

- `dashboard`: This is the time it takes to run `dashboard.py` and generate the `.html` document by the Panel server
- `fast` assets: Lots of *fast* `.js` and `.css` files that seem not to be *minimized*.

## Remove the bottlenecks

Some tips and tricks for removing bottlenecks identified are

- [] Prepare your data well
  - [] Load data from faster sources. For example `parquet` files instead of `csv` files or slow databases
  - [] Organize your data into small chunks that are fast to read when you need them
  - [] Reduce the size of your data. For example use `numpy.float32` instead of `numpy.float64` or categorical columns.
- [] Schedule background tasks to update your data
- [] Move code out of the file(s) you *serve*
- [] Pre-instantiate your static components and `--warm` your server
- [] Use caching! For example use `@pn.cache` or `pn.as_cached`.
- [] Defer the load
  - [] Indicate activity using progress bars and spinners to make the launch *feel* faster
- [] Use a Panel template that loads faster
- [] Use a `.html` template as your home `--index` page instead of a `.py` file
- [] Use a faster (i.e. more recent) version of Python
- [] Use faster libraries. For example Polars instead of Pandas
- [] Minimize the size of the images, data points etc. loaded on the client side
- [] Remove any not used `.js` extension libraries loaded by the client
- [] Use threading, multiprocessing or async to parallelize the processing.
- [] Use `--num-procs` to run multiple instances of the Panel server.
- [] Move processing away from the Panel server
  - [] To the client
  - [] To a REST API
  - [] To a database like Postgres or DuckDB
  - [] To a distributed analytics engine like Dask
  - [] To a distributed task queue like Celery
- [] Deploy each page of your multi-page app seperately
- [] Scale vertically by deploying on bigger or faster servers
- [] Scale horizontally by deploying to more servers
- [] Recommend your users to use a faster browser. For example Chrome over Firefox.
