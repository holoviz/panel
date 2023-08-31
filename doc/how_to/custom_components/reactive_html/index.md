# Create Custom Components with `ReactiveHTML`

These guides addresses how to create custom components with HTML, CSS and/ or Javascript using
`ReactiveHTML` and no Javascript build tools.

A `ReactiveHTML` subclass provides bi-directional syncing of its parameters with arbitrary HTML
elements, attributes and properties. The key part of the subclass is the `_template`
variable. This is the HTML template that gets rendered and declares how to link parameters on the
subclass to HTML.

---

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`columns-2;2.5em;sd-mr-1 sd-animate-grow50` Layouts
:link: reactive_html_layout
:link-type: doc

How to create layouts using `ReactiveHTML`
:::

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`brush;2.5em;sd-mr-1 sd-animate-grow50` Styling
:link: reactive_html_layout
:link-type: doc

How to style `ReactiveHTML` components
:::

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`bolt;2.5em;sd-mr-1 sd-animate-grow50` Callbacks
:link: reactive_html_callbacks
:link-type: doc

How to add Python and JS callbacks to `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`select;2.5em;sd-mr-1 sd-animate-grow50` Widgets
:link: reactive_html_widgets
:link-type: doc

How to create input widgets using `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`border-all;2.5em;sd-mr-1 sd-animate-grow50` DataFrame
:link: reactive_html_dataframe
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

## Related Resources

- Read the associated [Explanation > Building Custom Components](../../explanation/components/components_custom) to learn how `ReactiveHTML` works.

## External Resources

- [Building custom Panel widgets using ReactiveHTML | Blog post](https://blog.holoviz.org/building_custom_panel_widgets_using_reactivehtml.html)
- Read the [Param Documentation](https://param.holoviz.org/): learn more about `ReactiveHTML`s powerful parameters.
