# Reduce the launch time of your data app

In this *how to guide* we will provide tips and tricks for reducing the time it takes to launch your
app. This will improve the *user experience* and enable you to serve more users.

- "Studies show that 53% of mobile site visits are abandoned if pages take longer than 3 seconds to load!"
- "Two seconds is the threshold for eCommerce website acceptability. At Google, we aim for under a half-second."

In this guide we will focus on the scenario where a single user is launching your page at the time. Other guides will show you how to handle more complex scenarios with many users and many interactions.

Below we will explain how to identify and remove bottlenecks. But first you will need to understand
what happens when your app is launched.

## Understanding the launch

This is what happens when a user launches a page

- A user using a browser (client) **requests** the page
- The server **runs** the python file of the page and **generates** a html document
- The server **responds** by sending the html document to the client
- The client **receives** the html document, downloads the required assets and **renders** the document
- The client opens a **web socket connection** to the server
- Any **deferred components** are sent from the server to the client over the web socket
- The client receives the deferred components and **updates** the page

As you can see the bottlenecks can be

- on the server side,
- on the client side, or
- in the network between the server and client

## Install the requirements

```
pip install panel pandas plotly pyinstrument
```

## Create the reference multi-page app

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

The *Home* page looks like

![Home App](https://user-images.githubusercontent.com/42288570/212533365-ca493863-2a46-4107-beca-05d44830fa31.jpg)

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

The *Dashboard* page looks like

![Dashboard App](https://user-images.githubusercontent.com/42288570/212533385-8350e3d3-a1b7-4aa6-a125-6f50f66f7422.jpg)

Lets serve the apps with

```bash
panel serve home.py dashboard.py --index home
```

## Identify the bottlenecks

If you want to identify bottlenecks you can

- [] Use the [developer tools](https://developer.chrome.com/docs/devtools/network/) in the browser to measure the total time it takes to load and render your app.
- [] Use the `--admin` and the `--profiler` to identify bottlenecks on the server side
- [] Use pytest, pytest-benchmark and a profiler to identify bottlenecks on the server side. Todo: FIGURE OUT HOW DO I DO THIS? I need to setup the full flow. Something like `CodeRunner.run`.

### Identify bottlenecks using the developer tools

Here we will try to identify bottlenecks seen from the user and client side.

Please

- Open the *Dashboard* page at http://localhost:5006/dashboard
- Open the *Home* page at http://localhost:5006
- Open the developer tools and navigate to the *network* tab
- Hard refresh the *Home* page by holding the Ctrl key and clicking the Refresh button
- Sort the Network table by *Time* desc

On my laptop it looks like

![Home Developer Tools View](https://user-images.githubusercontent.com/42288570/212533878-c55ea350-da9a-4218-9a7f-10f7165ae481.jpg)

You see at the bottom that

- the total time it takes  finish loading the app is 1.75 seconds.
- The [DOMContent loaded event](https://developer.mozilla.org/en-US/docs/Web/API/Window/DOMContentLoaded_event) is loaded in 1.01 secs
- The [Window load event](https://developer.mozilla.org/en-US/docs/Web/API/Window/load_event) is fired in 1.01 secs

The key bottlenecks are

- `localhost`: This is the time it takes to run `home.py` and generate the `.html` document by the Panel server
- `data:image...`: This is the time it take to load the `.gif` image
- `plotly-2.10.1-min.js`: This is the time it takes to load the Plotly `.js` library which is not even used on this page!
- `fast` assets: Lots of *fast* `.js` and `.css` files that seem not to be *minimized*.

If we do the same for the *Dashboard* page we see

![Dashboard Developer Tools](https://user-images.githubusercontent.com/42288570/212534451-f65be0cb-7c42-4416-96b7-052d07dc4858.jpg)

The key bottlenecks are

- `dashboard`: This is the time it takes to run `dashboard.py` and generate the `.html` document by the Panel server
- `fast` assets: Lots of *fast* `.js` and `.css` files that seem not to be *minimized*.

### Identify more bottlenecks using the admin

Here we will try to identify bottlenecks seen from the server side.

Lets analyze the *Home* page

- Serve the apps `panel serve home.py dashboard.py --index home --admin --profiler pyinstrument`
- Open the *Home* page at http://localhost:5006/admin and reload it 9 times more. Please wait each time while the page loads.
- Open the *Admin* at http://localhost:5006/admin and change to the Launch Profiling page. Select the *Proportional Time*
- Close down the server

![home-admin.jpg](https://user-images.githubusercontent.com/42288570/212537748-246c0c0a-f00e-46f2-9cc4-5e4141555ff3.jpg)

You can see the big, big bottleneck is the `GIF` Pane where 82% of the time is spent!

Lets analyze the *Dashboard* page

- Serve the apps `panel serve home.py dashboard.py --index home --admin --profiler pyinstrument`
- Open the *Dashboard* page at http://localhost:5006/admin and reload it 9 times more. Please wait each time while the page loads.
- Open the *Admin* at http://localhost:5006/admin and change to the Launch Profiling page. Select the *Proportional Time*

![dashboard-admin.jpg](https://user-images.githubusercontent.com/42288570/212539034-ec29bd6a-b4e0-4a97-ae4d-a70eb77df0e2.jpg)

You can see the big 44% bottleneck is the `Plotly` Pane. This is in the Panel code though. The biggest bottleneck in our code is the 19% of the time spent on reading the data from the internet.

## Understand what is possible to achieve

You will not be able to launch your app in 0 seconds. So try to understand what the minimum launch time is.

Try measuring the time it takes to load the below benchmark app

```python
import panel as pn
pn.pane.Markdown("Hello World!").servable()
```

I get 233ms total and 23ms for the html page.

![hello-world-developer.jpg](https://user-images.githubusercontent.com/42288570/212541323-cbaa9e0e-c57d-4fdc-9263-f6442ff39e78.jpg)

Also try measuring the time it takes to load the below benchmark app

```python
from panel.pane.markup import Markdown
from panel.template.fast.list import FastListTemplate

FastListTemplate(
    main=[Markdown("Hello World!", sizing_mode="stretch_width")]
).servable()
```

I get 417ms total and 73ms for the html page.

This sets the lower limit for what we can expect to achieve.

## Remove the bottlenecks

Some tips and tricks for removing bottlenecks are

- [] Prepare your data well
  - [] Load data from faster sources. For example `parquet` files instead of `csv` files or slow databases
  - [] Partition your data into small chunks that are fast to read when you need them
  - [] Reduce the size of your data. For example use `numpy.float32` instead of `numpy.float64` or categorical columns.
- [] Schedule background tasks to update your data
- [] Remove unused imports and code
- [] Move code out of the file(s) you *serve* to seperate modules
- [] Pre-instantiate your static components and `--warm` your server
- [] Use caching! For example use `@pn.cache` or `pn.as_cached`.
- [] Defer the load
  - [] Using `pn.config.defer_load` or `pn.state.onload`.
  - [] By only loading the heavier stuff when the user starts interacting with the app. For by clicking a `submit` button.
  - [] By indicating activity using progress bars and spinners to make the launch *feel* faster
- [] Use a custom Panel template that loads faster or no template at all
- [] Use a script `.py` file instead of a notebook `.ipynb` file.
- [] Use a static `.html` page as the `--index` page instead of a `.py` file
- [] Use a faster (i.e. more recent) version of Python
- [] Use faster libraries. For example Polars instead of Pandas
- [] Don't use an image Pane. Its slow.
  - [] Use an `image` html tag in a `Markdown` or `HTML` pane.
- [] Minimize the size of the images, data etc. loaded on the client side
- [] Switch to an external CDN for serving the Panel assets
- [] Remove any not used `.js` extension libraries loaded by the client
- [] Use threading, multiprocessing or async to parallelize the processing.
- [] Move the processing away from the Panel server
  - [] To the client
  - [] To a faster database like Postgres or DuckDB
  - [] To a faster distributed analytics engine like Dask
  - [] To a faster distributed task queue like Celery
- [] Deploy your application on a bigger or faster server
- [] Recommend your users to use a faster browser. In my experience Chrome renders Panel apps faster than Firefox.
- [] Report general performance issues to Panel and/ or contribute improvements

## Use a HTML pane and `image` html tag instead of an image pane

## Use a static `.html` page as the `--index` page

We will first create the static `home.html` page from the below `home.py` file.

```python
# home.py
import panel as pn

pn.extension(sizing_mode="stretch_width")

SECTION = """
Panel works really well with the visualization tools you already know and love like [Altair/ Vega](https://panel.holoviz.org/reference/panes/Vega.html), [Bokeh](https://panel.holoviz.org/reference/panes/Bokeh.html), [Datashader](https://datashader.org/), [Deck.gl/ pydeck](https://panel.holoviz.org/reference/panes/DeckGL.html), [Echarts/ pyecharts](https://panel.holoviz.org/reference/panes/ECharts.html), [Folium](https://panel.holoviz.org/reference/panes/Folium.html), [HoloViews](https://holoviews.org/), [hvPlot](https://hvplot.holoviz.org), [plotnine](https://panel.holoviz.org/reference/panes/Matplotlib.html), [Matplotlib](https://panel.holoviz.org/reference/panes/Matplotlib.html), [Plotly](https://panel.holoviz.org/reference/panes/Plotly.html), [PyVista/ VTK](https://panel.holoviz.org/reference/panes/VTK.html), [Seaborn](https://panel.holoviz.org/gallery/styles/SeabornStyle.html) and more. Panel also works with the [ipywidgets](https://panel.holoviz.org/reference/panes/IPyWidget.html) ecosystem.

<img src="https://user-images.githubusercontent.com/42288570/211983400-3315ad0a-866a-4916-8809-6fc38eca34d9.gif" height=400 alt="Pythons DataViz works with Panel"></img>
"""

NAVIGATION = """
## Navigation

[home](home)
[dashboard](dashboard)
"""

pn.template.FastListTemplate(
    site="Panel", site_url="https:\\panel.holoviz.org",
    title="Home", main=[SECTION], sidebar=[NAVIGATION],
    main_max_width="900px",
).save("home.html")
```

Run `python home.py`.

Now change `.save("home.html")` to `.servable()` and run

```bash
panel serve home.py dashboard.py --index '/some/path/home.html'
```

Please note you will have to use the absolute path to the `home.html` due to [bug #4285](https://github.com/holoviz/panel/issues/4285).

In the *network* tab you will see something like

![Static Index Page](https://user-images.githubusercontent.com/42288570/212561757-428953a1-28c3-41b6-a212-abcc857f7cec.jpg)

You can see that

- the interaction with `localhost` is reduced to 4ms!
- the `.js` and `.css` files are no longer served by the Panel server.
- the `load` time is reduced from +1.01sec to 442msec.

Thus your Panel server will be able to handle more than 100 times as many users visiting your *Home* page compared to the initial *Home* page. And the users will have a much improved user experience.
