# Reduce the launch time of your data app

In this *how to guide* we will provide tips and tricks for reducing the time it takes to launch your
app. This will improve the *user experience* and enable you to serve more users with the same
resources.

In this guide we will focus on how you can improve the architecture and code of
your app.

Below we will explain how to identify and remove bottlenecks. But first you will need to understand
what happens when your app is launched.

## An example app

```python
import panel as pn
```

## Understanding the launch

- A user using a browser (client) **requests** the page
- The server **runs** the .py file of the page and **generates** a html document
- The server **responds** by sending the html document to the client
- The client **receives** the html document and **renders** it
- The client opens a **web socket connection** to the server
- Any **deferred components** are sent from the server to the client over the web socket
- The client receives the deferred components and **updates** the page

As you can see the bottlenecks can be in many places, and on both the server and client side.

## Identifying Bottlenecks

If you want to identify bottlenecks you can

- [] Manually measure the duration of specific parts of your app
- [] Use the admin and a profiler to identify bottlenecks on the server side
- [] Use Playwright with Loadwright to measure the launch time on the client side
- [] Analyze your users and forecast how they will be interacting with your app

## Removing Bottlenecks

Some tips and tricks for removing bottlenecks identified are

- [] Move code out of the file(s) you *serve*.
- [] Instantiate static Panel components once and for all
- [] `--warm` your server
- [] Use caching! Use caching! Use caching!
- [] Schedule background tasks to update your data
- [] Defer the load
- [] Load data from faster sources. For example `parquet` instead of `csv` files.
- [] Reduce the precision of your data. For example use `numpy.float32` instead of `numpy.float64`.
- [] Use a Panel template that loads faster
- [] Use faster libraries. For example Polars instead of Pandas
- [] Remove any not used `.js` extension libraries loaded by the client
- [] Use threading, multiprocessing or async to parallelize the processing.
- [] Move processing away from the Panel server
  - [] To the client
  - [] To a REST API
  - [] To a database like Postgres or DuckDB
  - [] To a distributed analytics engine like Dask
  - [] To a distributed task queue like Celery
- [] Use `--num-procs` to run multiple instances of the Panel server.
- [] Deploy each page of your multi-page app seperately behind a load balancer
- [] Scale vertically by deploying on bigger or faster servers
- [] Scale horizontally by deploying to more servers
