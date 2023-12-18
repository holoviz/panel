# Add concurrent processing

When deploying a Panel application to be accessed by multiple users they will often access the same server simultaneously. To maintain responsiveness of the application when multiple users are interacting with it at the same time there are multiple approaches to concurrency, each with their own drawbacks and advantages:

1. `Load balancing`: A load balancer distributes network traffic between multiple instances of the Panel application. This ensures that the load is distributed across multiple servers but also requires a lot configuration and resources.
2. `Multi-process server instance`: Launches your app with multiple processes on a single machine. Much simpler to set up than a load balancer but the load is not distributed equally across processes and you are limited by the compute and memory resources on one machine.
2. `Threading`: Attempts to distribute processing across multiple threads. Effectiveness depends on the operations being performed, I/O bound and CPU bound operations that release the GIL can easily be made concurrent in this way.
3. `AsyncIO`: Allows asynchronously processing I/O bound operations. Effective for many concurrent I/O operations but requires rewriting your application and callbacks to make use of `async`/`await` paradigm.

## Scaling across processes

Both load balancing and starting multiple processes effectively spin up multiple copies of the same application and distribute the load across the processes. This results in duplication and therefore significantly higher overhead (basically scaling linearly with the number of processes). In applications where you are relying on global state (e.g. the `pn.state.cache`) this can introduce significant challenges to ensure that application state stays synchronized.

::::{grid} 1 2 2 2
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`law;2.5em;sd-mr-1 sd-animate-grow50` Set up Load Balancing
:link: load_balancing
:link-type: doc

Discover how-to configure load balancing (e.g. using NGINX) to scale Panel apps across processes.
:::

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1 sd-animate-grow50` Launch multiple processes
:link: processes
:link-type: doc

Discover how to launch multiple processes on a Panel server to add scaling.
:::

::::

## Scaling within a single process

Threading and async are both approaches to speed up processing in Python using concurrency in a single Python process. Since we can't provide a complete primer on either threading or asynchronous processing here, if you are not familiar with these concepts we recommend reading up on them before continuing. Read about [threading in Python here](https://realpython.com/intro-to-python-threading/) and [AsyncIO here](https://realpython.com/async-io-python/).

When to use which approach cannot be answered easily and is never completely clear cut. As a general guide however use `asyncio` can scale almost arbitrarily allowing you to perform thousands or even millions of IO bound operations concurrently, while threading  limits you to the number of available threads. In practice this may never actually become relevant so the other main differences are that `async` coroutines are significantly more lightweight but that you have to carefully consider accessing shared objects across threads. Using `async` coroutines makes it very clear where concurrency occurs and therefore can make it easier to avoid race conditions and avoid having to think about locking a thread to access shared objects. However, in some situations threading can also be useful for CPU intensive operations where the operation being executed [releases the GIL](https://realpython.com/python-gil/), this includes many NumPy, Pandas and Numba functions.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`number;2.5em;sd-mr-1 sd-animate-grow50` Enable Automatic Threading
:link: threading
:link-type: doc

Discover how to enable threading to distribute processing across threads.
:::

:::{grid-item-card} {octicon}`stack;2.5em;sd-mr-1 sd-animate-grow50` Set up Manual Threading
:link: manual_threading
:link-type: doc

Discover how to manually set up a Thread to process an event queue.
:::

:::{grid-item-card} {octicon}`arrow-switch;2.5em;sd-mr-1 sd-animate-grow50` Use Asynchronous Processing
:link: ../callbacks/async
:link-type: doc

Discover how to make use of asynchronous callbacks to handle I/O and cpu bound operations concurrently.
:::

:::{grid-item-card} {octicon}`paper-airplane;2.5em;sd-mr-1 sd-animate-grow50` Sync to Async
:link: sync_to_async
:link-type: doc

Discover how to run your sync callbacks asynchronously to handle I/O and cpu bound operations concurrently.
:::

::::

## Scaling via an external compute engine

You can also scale your application by offloading your compute heavy tasks to an external compute engine like [Dask](https://www.dask.org/). Please note that this may add additional overhead of several 100ms to your tasks.

::::{grid} 1 2 2 2
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1 sd-animate-grow50` Dask
:link: dask
:link-type: doc

Discover how-to configure and use Dask to scale your Panel application
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

load_balancing
processes
threading
manual_threading
../callbacks/async
sync_to_async
dask
```
