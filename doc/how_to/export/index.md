# Export Apps

One of the main design goals for Panel was that it should make it possible to seamlessly transition back and forth between interactively prototyping a dashboard in the notebook or on the command line to deploying it as a standalone server app. This section shows how to display panels interactively, embed static output, save a snapshot, and deploy as a separate web-server app. For more information about deploying Panel apps to various cloud providers see the [Server Deployment](Server_Deployment.ipynb) documentation.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Embed state
:link: embedding
:link-type: doc

How to embed app state for usage entirely within Javascript.
:::

:::{grid-item-card} Save App to File
:link: saving
:link-type: doc

How to export an app to a HTML or PNG file.
:::

:::{grid-item-card} Access the Bokeh model
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
