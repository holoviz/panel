# Build Custom Components

These How-to pages provide solutions for common tasks related to extending Panel with custom components.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`git-merge;2.5em;sd-mr-1 sd-animate-grow50` Combine Existing Components
:link: custom_viewer
:link-type: doc

How to build custom components that are combinations of existing components.
:::

:::{grid-item-card} {octicon}`plus-circle;2.5em;sd-mr-1 sd-animate-grow50` Build Components from Scratch
:link: custom_reactiveHTML
:link-type: doc

How to build custom components with HTML, CSS, Javascript and `ReactiveHTML` and no Javascript tooling.
:::

::::

## Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Build a Plot Viewer
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/plot_viewer.png
:link: examples/plot_viewer
:link-type: doc

Build a custom component wrapping a bokeh plot and some widgets using the `Viewer` pattern.
:::

:::{grid-item-card} Build a Table Viewer
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/table_viewer.png
:link: examples/table_viewer
:link-type: doc

Build a custom component wrapping a table and some widgets using the `Viewer` pattern.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

custom_viewer
custom_reactiveHTML
```
