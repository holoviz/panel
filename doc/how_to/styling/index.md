# Style Components

Panel provides a comprehensive system for applying themes and custom styling to components.

## Theme and style `pn.ui` apps

The `pn.ui` components are built on Material UI. They are themed with `theme_config` and styled with `sx`.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`paintbrush;2.5em;sd-mr-1 sd-animate-grow50` Customize Themes and Styles
:link: ui_themes_and_styles
:link-type: doc

How to style `pn.ui` components with `sx`, `theme_config` and `styles`.
:::

:::{grid-item-card} {octicon}`circle;2.5em;sd-mr-1 sd-animate-grow50` Customize the Color Palette
:link: ui_palette
:link-type: doc

How to override and extend the color palette of `pn.ui` components.
:::

:::{grid-item-card} {octicon}`typography;2.5em;sd-mr-1 sd-animate-grow50` Customize Typography
:link: ui_typography
:link-type: doc

How to customize fonts, font sizes and text variants of `pn.ui` components.
:::

:::{grid-item-card} {octicon}`moon;2.5em;sd-mr-1 sd-animate-grow50` Control Dark Mode
:link: ui_dark_mode
:link-type: doc

How to force, toggle and customize dark mode for `pn.ui` components.
:::

:::{grid-item-card} {octicon}`eyedropper;2.5em;sd-mr-1 sd-animate-grow50` Pick Colors
:link: ui_pick_colors
:link-type: doc

How to choose a cohesive, accessible color palette for your theme.
:::

:::{grid-item-card} {octicon}`gear;2.5em;sd-mr-1 sd-animate-grow50` Theme Components
:link: ui_theme_components
:link-type: doc

How to customize `pn.ui` components app-wide with default props, style overrides and variants.
:::

:::{grid-item-card} {octicon}`briefcase;2.5em;sd-mr-1 sd-animate-grow50` Apply Branding
:link: ui_branding
:link-type: doc

How to build a cohesive branded app with brand colors, fonts, logos and theme configuration.
:::

:::{grid-item-card} {octicon}`smiley;2.5em;sd-mr-1 sd-animate-grow50` Use Icons
:link: ui_icons
:link-type: doc

How to use Material icons in components, Markdown and inline text.
:::

:::{grid-item-card} {octicon}`graph;2.5em;sd-mr-1 sd-animate-grow50` Theme Plotting Libraries
:link: ui_plotting_themes
:link-type: doc

How plots automatically follow the `pn.ui` theme, and how to match palettes and colormaps.
:::

::::

## Classic designs and CSS

The guides below apply to the classic `pn.widgets`, `pn.pane` and `pn.layout` components and templates, which are styled through designs, CSS variables and `stylesheets`.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`pencil;2.5em;sd-mr-1 sd-animate-grow50` Apply a Design
:link: design
:link-type: doc

How to switch between different design systems.
:::

:::{grid-item-card} {octicon}`sun;2.5em;sd-mr-1 sd-animate-grow50` Toggle themes
:link: themes
:link-type: doc

How to toggle between themes (e.g. 'light' and 'dark').
:::

:::{grid-item-card} {octicon}`gift;2.5em;sd-mr-1 sd-animate-grow50` Apply CSS
:link: apply_css
:link-type: doc

How to apply custom CSS styling.
:::

:::{grid-item-card} {octicon}`paintbrush;2.5em;sd-mr-1 sd-animate-grow50` Customize a Design
:link: design_variables
:link-type: doc

How to customize designs and themes with CSS variables.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1 sd-animate-grow50` Customize Loading Icon
:link: load_icon
:link-type: doc

How to customize the loading icon.
:::

:::{grid-item-card} {octicon}`eye;2.5em;sd-mr-1 sd-animate-grow50` Control Visibility
:link: visibility
:link-type: doc

How to control the visibility of a component.
:::

::::

This section will show you how to style the most common plotting libraries for use with Panel.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Altair
:link: altair
:link-type: doc

```{image} ../../_static/logos/altair-logo.png
:width: 125px
:align: center
:name: Altair
```

How to style an Altair plot
:::

:::{grid-item-card} ECharts
:link: echarts
:link-type: doc

```{image} ../../_static/logos/echarts-logo.png
:width: 125px
:align: center
:name: ECharts
```

How to style an ECharts plot
:::

:::{grid-item-card} Matplotlib
:link: matplotlib
:link-type: doc

```{image} ../../_static/logos/matplotlib-logo.png
:width: 125px
:align: center
:name: Matplotlib
```

How to style a Matplotlib plot
:::

:::{grid-item-card} Plotly
:link: plotly
:link-type: doc

```{image} ../../_static/logos/plotly-logo.png
:width: 125px
:align: center
:name: Plotly
```

How to style a Plotly plot
:::

:::{grid-item-card} Vega Lite
:link: vega
:link-type: doc

```{image} ../../_static/logos/vegalite-logo.png
:width: 125px
:align: center
:name: Vega
```

How to style a Vega Lite plot
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 1

ui_themes_and_styles
ui_palette
ui_typography
ui_dark_mode
ui_pick_colors
ui_theme_components
ui_branding
ui_icons
ui_plotting_themes
design
themes
apply_css
design_variables
load_icon
visibility
altair
echarts
matplotlib
plotly
vega
```
