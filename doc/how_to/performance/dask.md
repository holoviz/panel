# Scaling Panel apps with Dask

By combining Panel and Dask you can **scale your apps to bigger datasets, bigger calculations and more users**.

Compared to other data app frameworks Panel is novel in that it supports `async`. This means you can easily **offload large computations to your Dask cluster and keep your app responsive while you `await` the results**. This makes Panel and Dask a great combination.

Please note that some of the tools you can use with Panel have built in support for Dask.

- You can use `hvPlot` with Dask Dataframes simply by running `import hvplot.dask`.
- You can use `Holoviews` with Dask Dataframes and Arrays datasets.

## Installation

Lets start by installing *Panel*, *hvPlot* and *Dask Distributed*.

```bash
pip install panel hvplot dask[distributed]
```

## Local Configuration (Optional)

When you import the Dask `Client` in your Panel app it will change the log level of the Bokeh/ Panel server. Thus if you want to see logs, you will have to configure them.

One way to configure the log level is by adding or updating the file  ~/.config/dask/config.yaml

```yaml
# config.yaml
logging:
  distributed: info
  distributed.client: info
  bokeh: info
```

If you are behind a reverse proxy you will also have to set the *[Dask Daskboard](https://docs.dask.org/en/stable/dashboard.html) link*. For example
the author of this article is working on a Jupyterhub and needs to add

```yaml
distributed:
  dashboard:
    # This updates the dash dashboard links to proxy through jupyter-server-proxy
    link: /NAMESPACE/user/{JUPYTERHUB_USER}/proxy/{port}/status
```

## Tasks

The Dask `Client` will pickle any *tasks* and send them to the Dask `Cluster` for execution. This means that the `Client` and `Cluster` must able to import the same versions of all *tasks* and python package dependencies.

Lets put some *fibonacci* tasks in a shared `tasks.py` file

```python
# tasks.py
from datetime import datetime as dt

import numpy as np


def _fib(n):
    if n < 2:
        return n
    else:
        return _fib(n - 1) + _fib(n - 2)


def fibonacci(n):
    start = dt.now()
    print(start, "start", n)
    result = _fib(n)
    end = dt.now()
    print(end, "end", (end-start).seconds, n, result)
    return result
```

## Local Dask Cluster

For development, testing and simple use cases a `LocalCluster` is more than fine.

To avoid any issues when combining Panel and Dask we recommend starting the `LocalCluster`
seperately from the Dask `Client` and your Panel app.

You can do this by creating the file `cluster.py`

```python
# cluster.py
from dask.distributed import LocalCluster

DASK_SCHEDULER_PORT = 64719
DASK_SCHEDULER_ADDRESS = f"tcp://127.0.0.1:{DASK_SCHEDULER_PORT}"
N_WORKERS = 4

if __name__ == '__main__':
    cluster = LocalCluster(scheduler_port=DASK_SCHEDULER_PORT, n_workers=N_WORKERS)
    print(cluster.scheduler_address)
    input()
```

and running

```bash
$ python cluster.py
tcp://127.0.0.1:64719
```

You can now open the [Dask Dashboard](https://docs.dask.org/en/stable/dashboard.html) at http://localhost:8787/status.

The author is behind a reverse proxy on a JupyterHub and can open it at https://DOMAIN/NAMESPACE/user/USER_NAME/proxy/8787/status

So far there is not a lot to see

![Empty Dask Dashboard](https://user-images.githubusercontent.com/42288570/209457963-1e62cfe0-135a-45b6-844f-18a9a94f3ca4.jpg)

## Dask Dashboard Components

It can be very usefull to include some of the live [Dask endpoints](https://distributed.dask.org/en/stable/http_services.html) in your app. Its easy to do by embedding the specific urls in an *iframe*.

In the `dashboard.py` file we define the `DaskViewer` component that can be used to explore the *individual dask plots*.

```python
# dashboard.py
import os

import param

import panel as pn

DASK_DASHBOARD_ADDRESS = os.getenv("DASK_DASHBOARD", "http://localhost:8787/status")

VIEWS = {
    "aggregate-time-per-action": "individual-aggregate-time-per-action",
    "bandwidth-types": "individual-bandwidth-types",
    "bandwidth-workers": "individual-bandwidth-workers",
    "cluster-memory": "individual-cluster-memory",
    "compute-time-per-key": "individual-compute-time-per-key",
    "cpu": "individual-cpu",
    "exceptions": "individual-exceptions",
    "gpu-memory": "individual-gpu-memory",
    "gpu-utilization": "individual-gpu-utilization",
    "graph": "individual-graph",
    "groups": "individual-groups",
    "memory-by-key": "individual-memory-by-key",
    "nprocessing": "individual-nprocessing",
    "occupancy": "individual-occupancy",
    "profile-server": "individual-profile-server",
    "profile": "individual-profile",
    "progress": "individual-progress",
    "scheduler-system": "individual-scheduler-system",
    "task-stream": "individual-task-stream",
    "workers-cpu-timeseries": "individual-workers-cpu-timeseries",
    "workers-disk-timeseries": "individual-workers-disk-timeseries",
    "workers-disk": "individual-workers-disk",
    "workers-memory-timeseries": "individual-workers-memory-timeseries",
    "workers-memory": "individual-workers-memory",
    "workers-network-timeseries": "individual-workers-network-timeseries",
    "workers-network": "individual-workers-network",
    "workers": "individual-workers",
}

VIEWER_PARAMETERS = ["url", "path"]

def to_iframe(url):
    return f"""<iframe src="{url}" frameBorder="0" style="height:100%;width:100%"></iframe>"""

class DaskViewer(pn.viewable.Viewer):
    url = param.String(DASK_DASHBOARD_ADDRESS, doc="The url of the Dask status dashboard")
    path = param.Selector(default="individual-cpu", objects=VIEWS, doc="the endpoint", label="View")

    def __init__(self, size=20, **params):
        viewer_params = {k:v for k, v in params.items() if k in VIEWER_PARAMETERS}
        layout_params = {k:v for k, v in params.items() if k not in VIEWER_PARAMETERS}

        self._iframe =  pn.pane.HTML(sizing_mode="stretch_both")
                
        super().__init__(**viewer_params)

        self._select = pn.widgets.Select.from_param(self.param.path, size=size, width=300, sizing_mode="fixed", margin=(20,5,10,5))
        self._link = pn.panel(f"""<a href="{DASK_DASHBOARD_ADDRESS}" target="_blank">Dask Dashboard</a>""", height=50, margin=(0,20))
        self._panel = pn.Column(pn.Row(self._iframe, self._select, sizing_mode="stretch_both"), self._link, **layout_params)


    @pn.depends("url", "path", watch=True, on_init=True)
    def _update_panel(self):
        url = self.url.replace("/status", "/") + self.path
        self._iframe.object = to_iframe(url)

    def __panel__(self):
        return self._panel

if __name__.startswith("bokeh"):
    pn.extension(sizing_mode="stretch_width")

    DaskViewer(height=500, size=25).servable()
```

Try running `panel serve dashboard.py`. If your Dask cluster is working, you will see something like

![Dask Viewer](https://user-images.githubusercontent.com/42288570/209478790-518309e3-1fe3-4d92-a54d-76259796504c.gif)

## Async/Await and Non-Blocking Execution

This approach is great if you want to offload larger computations to Dask while keeping your Panel data app responsive. Please note that off loading the computations to the Dask cluster adds ~250msec of overhead and thus is not suitable for all kinds of use cases.

In this section we will define a Panel app to *submit* and *monitor* Fibonacci tasks.

Lets discuss a few *key ideas* of the app

- We can instantiate and share a Dask Client asynchronously using `pn.state.cache`.

```python
async def get_client():
    if not "dask-client" in pn.state.cache:
        pn.state.cache["dask-client"] = await Client(
            DASK_SCHEDULER_ADDRESS, asynchronous=True
        )
    return pn.state.cache["dask-client"]
```

- We can submit Fibonacci tasks asynchronusly via

```python
client = await get_client()
fib_n = await client.submit(fibonacci, n)
```

Lets now define the full `app.py` file.

```python
# app.py
from datetime import datetime as dt

import param

from dashboard import DASK_DASHBOARD_ADDRESS, DaskViewer
from dask.distributed import Client

import panel as pn

from cluster import DASK_SCHEDULER_ADDRESS
from tasks import fibonacci

QUEUE = []

pn.extension("terminal", sizing_mode="stretch_width")


async def get_client():
    if not "dask-client" in pn.state.cache:
        pn.state.cache["dask-client"] = await Client(
            DASK_SCHEDULER_ADDRESS, asynchronous=True
        )
    return pn.state.cache["dask-client"]


n_input = pn.widgets.IntInput(value=0, width=100, sizing_mode="fixed", name="n")
submit_button = pn.widgets.Button(name="Submit", button_type="primary", align="end")
queue_widget = pn.widgets.LiteralInput(value=QUEUE, name="In Progress", disabled=True)
terminal_widget = pn.widgets.Terminal(
    height=200,
)
dask_viewer = DaskViewer(height=500)


@pn.depends(submit_button, watch=True)
async def _handle_click(_):
    n = n_input.value
    n_input.value += 1

    start = dt.now()
    QUEUE.append(n)
    queue_widget.value = QUEUE.copy()

    client = await get_client()
    fib_n = await client.submit(fibonacci, n)

    end = dt.now()
    QUEUE.pop(QUEUE.index(n))
    queue_widget.value = QUEUE.copy()
    duration = (end - start).seconds
    terminal_widget.write(f"fibonacci({n})={fib_n} in {duration}sec\n")


component = pn.Column(
    "## Tasks",
    pn.Row(n_input, submit_button),
    queue_widget,
    "## Results",
    terminal_widget,
    "## Dask Dashboard",
    dask_viewer,
)

pn.template.FastListTemplate(
    site="Panel + Dask", title="Async background tasks", main=[component]
).servable()
```

You can now run `panel serve app.py` and the app will look like

![Panel Dask Async Tasks](https://user-images.githubusercontent.com/42288570/209510282-e98f048a-0ad3-4ede-a6c4-c6eef9d11fa6.gif).

You might find additional inspiration in [Panel - Async and Concurrency](../../user_guide/Async_and_Concurrency.ipynb), [Dask - Async/Await and Non-Blocking Execution Documentation](https://examples.dask.org/applications/async-await.html#Async/Await-and-Non-Blocking-Execution) and [Dask - Async Web Server](https://examples.dask.org/applications/async-web-server.html).