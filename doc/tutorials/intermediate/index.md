# Intermediate Tutorials

These tutorials are for those that is ready to navigate and explore more advanced features of Python and Panel.

Together, we will build more performant, scalable, polished, reusable and maintainable versions of the applications from the basic tutorial.

After these tutorials you will be able to build a wide range of large and complex multi-page apps structured across multiple files using a *class based approach* and more advanced Python features like `async`.

I will assume you have a *basic skill level* corresponding to the what you get from the [Basic Tutorials](../basic/index.md).

## Get Started

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Serve Panel Apps
:link: serve
:link-type: doc

Learn to serve multi-page apps and how-to customize the Panel server.
:::

::::

## Develop Seamlessly

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Develop in an Editor
:link: develop_editor
:link-type: doc

Learn how to debug applications in an Editor
:::

::::

## Handle User Input

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`table;2.5em;sd-mr-1` Accept User Input from tables
:link: table_events
:link-type: doc

Elevate our app's functionality by accepting user input from tables.
:::

:::{grid-item-card} {octicon}`graph;2.5em;sd-mr-1` Accept User Input from plots
:link: plot_events
:link-type: doc

Elevate our app's functionality by accepting user input from plots.
:::

::::

## Structure Applications

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Structure with DataStore
:link: structure_data_store
:link-type: doc

Learn how to structure larger applications with the `DataStore` pattern
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

serve
develop_editor
table_events
plot_events
structure_data_store
```

## COMING UP

- Work with Parameters and Events: Param
- Organize Components flexibly with FlexBox
- Schedule Tasks: pn.state.onload, pn.state.schedule_task, pn.state.add_periodic_callback, pn.state.on_session_created, pn.state.on_session_destroyed, async generators, pn.state.execute
- Build custom components easily: Viewable
- Sync location
- Add interactivity flexibly: `.rx`
- Add side effects: `.watch` (or `watch=True` ?)
- Avoid Common Mistakes: Defining "global" widgets in utility modules that ends up being shared between users.
- Show progress dynamically with generators
- Enable Throtttling
- Share your work: Embed, Save, link to other deployment options including WASM
- Build maintainable apps: Class based approach, `@pn.depends`
- Organizing your code: How to organize the code into sections or modules for efficient maintenance and reuse (data, models, plots, components, app).
- Improve performance by using async and threads
- Testing
