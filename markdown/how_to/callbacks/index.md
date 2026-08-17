# Register Session Callbacks

These How-to pages provide solutions for common tasks related to setting up callbacks on session related events (e.g. on page load or when a session is destroyed) and defining periodic tasks.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: async
:link-type: doc

How to leverage asynchronous callbacks to run I/O bound tasks in parallel.
:::

:link: defer_load
:link-type: doc

How to defer execution of bound and displayed functions until the application is loaded with `defer_load`.
:::

:link: load
:link-type: doc

How to set up callbacks to defer a task until the application is loaded with `pn.state.onload`.
:::

:link: periodic
:link-type: doc

How to set up per-session callbacks that run periodically.
:::

:link: session
:link-type: doc

How to set up callbacks when a session is created and destroyed.
:::

:link: schedule
:link-type: doc

How to schedule tasks that run independently of any user visiting an application.
:::

:link: server
:link-type: doc

How to safely modify Bokeh models to avoid running into issues with the Bokeh `Document` lock.
:::

:link: notifications
:link-type: doc

How to add notifications when the application is ready and when it loses the server connection.
:::

::::

## Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:img-top: https://assets.holoviz.org/panel/how_to/callbacks/streaming_bokeh.png
:link: examples/streaming_bokeh
:link-type: doc

Use `add_periodic_callback` to stream data to a Bokeh plot.
:::

:img-top: https://assets.holoviz.org/panel/how_to/callbacks/streaming_indicator.png
:link: examples/streaming_indicator
:link-type: doc

Use `add_periodic_callback` to stream data to `Trend` indicators.
:::

:img-top: https://assets.holoviz.org/panel/how_to/callbacks/streaming_perspective.png
:link: examples/streaming_perspective
:link-type: doc

Use `add_periodic_callback` to stream data to a `Perspective` pane.
:::

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
