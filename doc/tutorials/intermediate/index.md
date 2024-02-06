# Intermediate Tutorials

These tutorials are for those that is ready to navigate and explore more advanced features of Python and Panel.

Together, we will build more performant, scalable, polished, reusable and maintainable versions of the applications from the basic tutorial.

After these tutorials you will be able to build a wide range of large and complex multi-page apps structured across multiple files using a *class based approach* and more advanced Python features like `async`.

## Prerequisites

We assume a *basic level of Panel skills* corresponding to the skills that can be acquired from the [Basic Tutorial](../basic/index.md).

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

## Organize Content

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`screen-full;2.5em;sd-mr-1` Control the Size
:link: size
:link-type: doc

We will discover how how to achieve truly responsive sizing with the FlexBox. We will use *media queries* to support different devices.
:::

::::

## Handle User Input

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`table;2.5em;sd-mr-1` Accept Inputs from tables
:link: table_events
:link-type: doc

Elevate our app's functionality by accepting user input from tables.
:::

:::{grid-item-card} {octicon}`graph;2.5em;sd-mr-1` Accept Inputs from plots
:link: plot_events
:link-type: doc

Elevate our app's functionality by accepting user input from plots.
:::

::::

## Improve the look

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`paintbrush;2.5em;sd-mr-1` Use Styles
:link: style
:link-type: doc

Fine-tune the styling of our components with `styles` and `stylesheets`. This will ensure our wind turbine data apps are both aesthetically pleasing and user-friendly.
:::

:::{grid-item-card} {octicon}`image;2.5em;sd-mr-1` Build a Polished Dashboard
:link: build_polished_dashboard
:link-type: doc

We'll guide you through advanced styling, layout optimization, and data visualization techniques to build a refined Wind Turbine Dashboard.
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
size
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
