# Create Custom Components with `ReactiveHTML`

These guides addresses how to create custom components with HTML, CSS and/ or Javascript using
`ReactiveHTML` and no Javascript tooling.

If you are not familiar with HTML, CSS or Javascript then the [W3 HTML School](https://www.w3schools.com/html/default.asp),
[W3 CSS School](https://www.w3schools.com/css/default.asp) and [W3 JS School](https://www.w3schools.com/js/default.asp)
are good resource to learn from. You can also ask ChatGPT for help. It can often provide you with
HTML, CSS and/ or Javascript that you can fine tune.

`ReactiveHTML` as most of Panel builds on top of [Param](https://param.holoviz.org/). If you are
not familiar with Param you should check out the [Param Documentation]](https://param.holoviz.org/).

---

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`rocket;2.5em;sd-mr-1 sd-animate-grow50` Layouts
:link: get_started
:link-type: reactive_html_layout

How to create layouts using HTML and `ReactiveHTML`
:::

:::{grid-item-card} {octicon}`device-desktop;2.5em;sd-mr-1 sd-animate-grow50` CSS Styling
:link: panes
:link-type: reactive_html_styling

How to style your `ReactiveHTML` components using CSS
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

reactive_html_layout
reactive_html_styling
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

- Read the associated [Explanation > Building Custom Components](../../explanation/components/components_custom) for further explanation.
