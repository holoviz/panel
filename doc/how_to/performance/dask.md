# Scaling Panel apps with Dask

This guide demonstrates how you can use Panel together with Dask to **scale your apps to bigger datasets, bigger calculations and more users**.

---

Compared to other data app frameworks Panel is novel in that it supports `async`. This means you can easily **offload large computations to your Dask cluster and keep your app responsive while you `await` the results**. This makes Panel and Dask a great combination.

Also note that some of the tools you can use with Panel have built in support for Dask:

- You can use `hvPlot` with Dask Dataframes simply by running `import hvplot.dask`.
- You can use `Holoviews` with Dask Dataframes and Arrays datasets.

Also some of the inbuilt analytics tools in Dask are built on Bokeh and can therefore be easily embedded in your Panel app.

## Installation

Lets start by installing *Panel*, *hvPlot* and *Dask Distributed*.

```bash
pip install panel hvplot dask[distributed]
```

## Tasks

The Dask `Client` will serialize any *tasks* and send them to the Dask `Cluster` for execution. This means that the `Client` and `Cluster` must able to import the same versions of all *tasks* and python package dependencies.

Let's start by defining some *fibonacci* tasks in a shared `tasks.py` file:

.. literalinclude:: ./dask/tasks.py

## Local Dask Cluster

For development, testing and simple use cases a `LocalCluster` is more than fine and will allow you to leverage all the CPUs on your machine. When you want to scale out to an entire cluster will you can switch to a non-local cluster. To avoid any issues when combining Panel and Dask we recommend starting the `LocalCluster`
separately from the Dask `Client` and your Panel app.

You can do this by creating the file `cluster.py` that looks like this:

.. literalinclude:: ./dask/cluster.py

and running

```bash
$ python cluster.py
tcp://127.0.0.1:64719
```

You can now open the [Dask Dashboard](https://docs.dask.org/en/stable/dashboard.html) at http://localhost:8787/status.

So far there is not a lot to see here:

![Empty Dask Dashboard](https://user-images.githubusercontent.com/42288570/209457963-1e62cfe0-135a-45b6-844f-18a9a94f3ca4.jpg)

## Dask Dashboard Components

It can be very useful to include some of the live [Dask endpoints](https://distributed.dask.org/en/stable/http_services.html) in your app. Its easy to do by embedding the specific urls in an *iframe*.

In the `dashboard.py` file we define the `DaskViewer` component that can be used to explore the *individual dask plots*.

.. literalinclude:: ./dask/dashboard.py

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

- We can submit Fibonacci tasks asynchronously via

```python
client = await get_client()
fib_n = await client.submit(fibonacci, n)
```

Lets now define the full `app.py` file.

.. literalinclude:: ./dask/app.py

You can now run `panel serve app.py` and the app will look like

![Panel Dask Async Tasks](https://user-images.githubusercontent.com/42288570/209510282-e98f048a-0ad3-4ede-a6c4-c6eef9d11fa6.gif).

You might find additional inspiration in [Panel - Async and Concurrency](../../user_guide/Async_and_Concurrency.ipynb), [Dask - Async/Await and Non-Blocking Execution Documentation](https://examples.dask.org/applications/async-await.html#Async/Await-and-Non-Blocking-Execution) and [Dask - Async Web Server](https://examples.dask.org/applications/async-web-server.html).
