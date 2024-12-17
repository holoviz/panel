# Export Apps

While Panel is primarily a library for building applications [backed by server](../server/index) or a [Python process in the browser](../wasm/index) it is sometimes useful to export static output, with or without embedded state to add interactivity. This section focuses on exporting Panel as static snapshots, embedding state and accessing the underlying Bokeh models.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`gift;2.5em;sd-mr-1 sd-animate-grow50` Embed state
:link: embedding
:link-type: doc

How to embed app state for usage entirely within Javascript.
:::

:::{grid-item-card} {octicon}`file;2.5em;sd-mr-1 sd-animate-grow50` Save App to File
:link: saving
:link-type: doc

How to export an app to a HTML or PNG file.
:::

:::{grid-item-card} {octicon}`sun;2.5em;sd-mr-1 sd-animate-grow50` Access the Bokeh model
:link: bokeh
:link-type: doc

How to access the underlying Bokeh model of Panel objects.
:::

::::



```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

embedding
saving
bokeh
```
