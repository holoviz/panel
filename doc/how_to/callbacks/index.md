# Register Session Callbacks

These How-to pages provide solutions for common tasks related to setting up callbacks on session related events (e.g. on page load or when a session is destroyed) and defining periodic tasks.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Use Asynchronous Callbacks
:link: async
:link-type: doc

How to leverage asynchronous callbacks to run I/O bound tasks in parallel.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1` Defer Callbacks Until Load
:link: load
:link-type: doc

How to set up callbacks to defer a task until the application is loaded.
:::

:::{grid-item-card} {octicon}`sync;2.5em;sd-mr-1` Periodically Run Callbacks
:link: periodic
:link-type: doc

How to set up per-session callbacks that run periodically.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Run Tasks at Session Start or End
:link: session
:link-type: doc

How to set up callbacks when a session is created and destroyed.
:::

:::{grid-item-card} {octicon}`calendar;2.5em;sd-mr-1` Schedule Global Tasks
:link: schedule
:link-type: doc

How to schedule tasks that run independently of any user visiting an application.
:::

:::{grid-item-card} {octicon}`lock;2.5em;sd-mr-1` Modify Bokeh Models
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
