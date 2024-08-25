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

### Examples

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
examples/plot_viewer
examples/table_viewer
```

## ESM Components

Build custom components in Javascript using so called ESM components, which allow you to write components that automatically sync parameter state between Python and JS. ESM components can be written in pure JavaScript, using [React](https://react.dev/) or using the [AnyWidget](https://anywidget.dev/) specification.

ESM Components is our 2nd generation api for custom components while `ReactiveHTML` is our 1st generation. We recommend using ESM Components over `ReactiveHTML`.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`columns;2.5em;sd-mr-1 sd-animate-grow50` Layouts
:link: esm/custom_layout
:link-type: doc

How to create custom layouts using ESM components
:::

:::{grid-item-card} {octicon}`arrow-left;2.5em;sd-mr-1 sd-animate-grow50` Callbacks
:link: esm/callbacks
:link-type: doc

How to add JS and Python based callbacks to ESM components.
:::

:::{grid-item-card} {octicon}`single-select;2.5em;sd-mr-1 sd-animate-grow50` Widgets
:link: esm/custom_widgets
:link-type: doc

How to create input widgets using ESM components
:::

:::{grid-item-card} {octicon}`table;2.5em;sd-mr-1 sd-animate-grow50` DataFrame
:link: esm/dataframe
:link-type: doc

How to create ESM components that render data a DataFrame.
:::

::::

### Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Canvas `JSComponent`
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/canvas_draw.png
:link: examples/esm_canvas
:link-type: doc

Build a custom component to draw on an HTML canvas based on `JSComponent`.
:::

:::{grid-item-card} Leaflet.js `JSComponent`
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/leaflet.png
:link: examples/esm_leaflet
:link-type: doc

Build a custom component wrapping leaflet.js using `JSComponent`.
:::

:::{grid-item-card} Material UI `ReactComponent`
:img-top: https://assets.holoviz.org/panel/how_to/custom_components/material_ui.png
:link: examples/esm_material_ui
:link-type: doc

Build custom components wrapping Material UI using `ReactComponent`.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

esm/callbacks
esm/custom_widgets
esm/custom_layout
esm/dataframe
examples/esm_canvas
examples/esm_leaflet
examples/esm_material_ui

```

## `ReactiveHTML` Components

Build custom components using HTML, CSS and Javascript and without Javascript build tools.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`columns;2.5em;sd-mr-1 sd-animate-grow50` Layouts
:link: reactive_html/reactive_html_layout
:link-type: doc

How to create layouts using `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`paintbrush;2.5em;sd-mr-1 sd-animate-grow50` Styling
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

:::{grid-item-card} {octicon}`arrow-left;2.5em;sd-mr-1 sd-animate-grow50` Callbacks
:link: reactive_html/reactive_html_callbacks
:link-type: doc

How to add Python and JS callbacks to `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`single-select;2.5em;sd-mr-1 sd-animate-grow50` Widgets
:link: reactive_html/reactive_html_widgets
:link-type: doc

How to create input widgets using `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`table;2.5em;sd-mr-1 sd-animate-grow50` DataFrame
:link: reactive_html/reactive_html_dataframe
:link-type: doc

How to create `ReactiveHTML` components that render data a DataFrame.

:::

::::

### Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

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

reactive_html/reactive_html_layout
reactive_html/reactive_html_styling
reactive_html/reactive_html_panes
reactive_html/reactive_html_indicators
reactive_html/reactive_html_callbacks
reactive_html/reactive_html_widgets
reactive_html/reactive_html_dataframe
examples/canvas_draw
examples/leaflet
examples/vue
```
