# Export Apps

While Panel is primarily a library for building applications [backed by server](../server/index) or a [Python process in the browser](../wasm/index) it is sometimes useful to export static output, with or without embedded state to add interactivity. This section focuses on exporting Panel as static snapshots, embedding state and accessing the underlying Bokeh models.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: embedding
:link-type: doc

How to embed app state for usage entirely within Javascript.
:::

:link: saving
:link-type: doc

How to export an app to a HTML or PNG file.
:::

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
