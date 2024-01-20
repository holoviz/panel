# Build Custom Components

These How-to pages provide solutions for common tasks related to extending Panel with custom components.

## `Viewer` Components

Build custom components by combining existing components.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`git-merge;2.5em;sd-mr-1 sd-animate-grow50` Combine Existing Components
:link: custom_viewer
:link-type: doc

How to build custom components that are combinations of existing components.
:::

::::

## `ReactiveHTML` Components

Build custom components using HTML, CSS and Javascript and without Javascript build tools.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`columns-2;2.5em;sd-mr-1 sd-animate-grow50` Layouts
:link: reactive_html/reactive_html_layout
:link-type: doc

How to create layouts using `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`brush;2.5em;sd-mr-1 sd-animate-grow50` Styling
:link: reactive_html/reactive_html_styling
:link-type: doc

How to style `ReactiveHTML` components
:::

:::{grid-item-card} {octicon}`image;2.5em;sd-mr-1 sd-animate-grow50` Panes
:link: reactive_html/reactive_html_panes
:link-type: doc

How to create panes using `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`issue-draft;2.5em;sd-mr-1 sd-animate-grow50` Indicators
:link: reactive_html/reactive_html_indicators
:link-type: doc

How to create indicators using `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`bolt;2.5em;sd-mr-1 sd-animate-grow50` Callbacks
:link: reactive_html/reactive_html_callbacks
:link-type: doc

How to add Python and JS callbacks to `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`select;2.5em;sd-mr-1 sd-animate-grow50` Widgets
:link: reactive_html/reactive_html_widgets
:link-type: doc

How to create input widgets using `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`border-all;2.5em;sd-mr-1 sd-animate-grow50` DataFrame
:link: reactive_html/reactive_html_dataframe
:link-type: doc

How to create components using `ReactiveHTML` and a DataFrame parameter
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

reactive_html_layout
reactive_html_styling
reactive_html_widgets
```

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

:::{grid-item-card} Build a Canvas component
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/canvas_draw.png
:link: examples/canvas_draw
:link-type: doc

Build a custom component to draw on an HTML canvas based on `ReactiveHTML`.
:::

:::{grid-item-card} Wrap Leaflet.js
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/leaflet.png
:link: examples/leaflet
:link-type: doc

Build a custom component wrapping leaflet.js using `ReactiveHTML`.
:::

:::{grid-item-card} Wrap Material UI
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/material_ui.png
:link: examples/material_ui
:link-type: doc

Build custom components wrapping material UI using `ReactiveHTML`.
:::

:::{grid-item-card} Wrap a Vue.js component
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/vue.png
:link: examples/vue
:link-type: doc

Build custom component wrapping a Vue.js app using `ReactiveHTML`.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

custom_viewer
custom_reactiveHTML
```
