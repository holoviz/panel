# Session callbacks and events

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Asynchronous callbacks
:link: async
:link-type: doc

How to leverage asynchronous callbacks to run I/O bound tasks in parallel.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Load callbacks
:link: session
:link-type: doc

How to set up callbacks to defer a task until the application is loaded.
:::

:::{grid-item-card} {octicon}`sync;2.5em;sd-mr-1` Periodic callbacks
:link: periodic
:link-type: doc

How to set up per-session callbacks that run periodically.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Session callbacks
:link: session
:link-type: doc

How to set up callbacks when a session is created and destroyed.
:::

:::{grid-item-card} {octicon}`calendar;2.5em;sd-mr-1` Schedule Tasks
:link: schedule
:link-type: doc

How to schedule tasks that run independently of any user visiting the application(s).
:::

:::{grid-item-card} {octicon}`lock;2.5em;sd-mr-1` Bokeh Server callbacks
:link: server
:link-type: doc

How to safely modify Bokeh models to avoid running into issues with the Bokeh `Document` lock.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

async
load
session
periodic
schedule
server
```
