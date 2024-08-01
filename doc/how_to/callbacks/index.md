# Register Session Callbacks

These How-to pages provide solutions for common tasks related to setting up callbacks on session related events (e.g. on page load or when a session is destroyed) and defining periodic tasks.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`arrow-switch;2.5em;sd-mr-1 sd-animate-grow50` Use Asynchronous Callbacks
:link: async
:link-type: doc

How to leverage asynchronous callbacks to run I/O bound tasks in parallel.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1 sd-animate-grow50` Defer Bound Functions Until Load
:link: defer_load
:link-type: doc

How to defer execution of bound and displayed functions until the application is loaded with `defer_load`.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1 sd-animate-grow50` Defer Callbacks Until Load
:link: load
:link-type: doc

How to set up callbacks to defer a task until the application is loaded with `pn.state.onload`.
:::

:::{grid-item-card} {octicon}`sync;2.5em;sd-mr-1 sd-animate-grow50` Periodically Run Callbacks
:link: periodic
:link-type: doc

How to set up per-session callbacks that run periodically.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1 sd-animate-grow50` Run Tasks at Session Start or End
:link: session
:link-type: doc

How to set up callbacks when a session is created and destroyed.
:::

:::{grid-item-card} {octicon}`calendar;2.5em;sd-mr-1 sd-animate-grow50` Schedule Global Tasks
:link: schedule
:link-type: doc

How to schedule tasks that run independently of any user visiting an application.
:::

:::{grid-item-card} {octicon}`lock;2.5em;sd-mr-1 sd-animate-grow50` Modify Bokeh Models
:link: server
:link-type: doc

How to safely modify Bokeh models to avoid running into issues with the Bokeh `Document` lock.
:::

:::{grid-item-card} {octicon}`link;2.5em;sd-mr-1 sd-animate-grow50` Connection Notifications
:link: notifications
:link-type: doc

How to add notifications when the application is ready and when it loses the server connection.
:::

::::

## Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Streaming Bokeh
:img-top: https://assets.holoviz.org/panel/how_to/callbacks/streaming_bokeh.png
:link: examples/streaming_bokeh
:link-type: doc

Use `add_periodic_callback` to stream data to a Bokeh plot.
:::

:::{grid-item-card} Streaming Indicators
:img-top: https://assets.holoviz.org/panel/how_to/callbacks/streaming_indicator.png
:link: examples/streaming_indicator
:link-type: doc

Use `add_periodic_callback` to stream data to `Trend` indicators.
:::

:::{grid-item-card} Streaming Perspective
:img-top: https://assets.holoviz.org/panel/how_to/callbacks/streaming_perspective.png
:link: examples/streaming_perspective
:link-type: doc

Use `add_periodic_callback` to stream data to a `Perspective` pane.
:::

:::{grid-item-card} Streaming Tabulator
:img-top: https://assets.holoviz.org/panel/how_to/callbacks/streaming_tabulator.png
:link: examples/streaming_tabulator
:link-type: doc

Use `add_periodic_callback` to stream data to a `Tabulator` widget.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

async
defer_load
load
session
periodic
schedule
server
notifications
```
