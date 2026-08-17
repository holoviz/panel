# Explanation

The explanation section aims to clarify, deepen, and broaden the understanding of Panel with discussions about topics at a high-level or from alternate angles. This may include reasoning about design decisions, historical development, and technical constraints.

Beyond the [Getting Started > Core Concepts](../getting_started/core_concepts.md), which new users must complete before working with Panel, this explanation section is intended to help practitioners form and strengthen a conceptual web that facilitates new and advanced usage directions.

## Developing in Panel

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: develop_seamlessly
:link-type: doc

Learn how we enable you and your team to work seamlessly with Panel across a wide range of development environments
:::

::::

## APIs

In this section we will discuss the principles and design decisions behind Panel's APIs in order to guide you towards the best approach for structuring your applications. We begin with a set of explanations behind the use of Param in Panel, how it unlocks reactive approaches to write applications and contrast function and class based approaches for writing apps.

::::{grid} 1 1 3 3
:gutter: 1 1 1 2

:link: api/param
:link-type: doc

Background on the use of Param in Panel.
:::

:link: api/reactivity
:link-type: doc

A deep dive into the reactive and callback based APIs in Panel.
:::

:link: api/functions_vs_classes
:link-type: doc

A discussion that contrasts function and class based APIs in Panel.
:::

::::

Next let us contrast the different APIs offered by Panel by applying them to a particular problem.

::::{grid} 1 1 3 3
:gutter: 1 1 1 2

:link: api/reactive
:link-type: doc

Linking functions or methods to widgets using `pn.bind` or the equivalent `pn.depends` decorator.
:::

:link: api/parameterized
:link-type: doc

Declare *Parameters* and their ranges in `Parameterized` classes, then get GUIs (and value checking!) for free.
:::

:link: api/callbacks
:link-type: doc

Generate a UI by manually declaring callbacks that update panels or panes.
:::

::::

Finally let's look at some examples demonstrating how each API can be applied to build the same app:

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:img-top: https://assets.holoviz.org/panel/how_to/apis/stocks_callback.png
:link: api/examples/stocks_callbacks
:link-type: doc

Build a stock explorer app using the `.param.watch` callback API.
:::

:img-top: https://assets.holoviz.org/panel/how_to/apis/stocks_declarative.png
:link: api/examples/stocks_declarative
:link-type: doc

Build a stock explorer app using the Param based declarative API.
:::

:img-top: https://assets.holoviz.org/panel/how_to/apis/stocks_reactive.png
:link: api/examples/stocks_reactive
:link-type: doc

Build a stock explorer app using the reactive API.
:::

:link: api/examples/outliers_declarative
:link-type: doc

Build a simple outlier explorer app using the declarative API.
:::

::::

## Components

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: components/components_overview
:link-type: doc

Deepen your understanding about Panel's built in components.
:::

:link: components/reactive_html_components
:link-type: doc

Deepen your understanding about custom `ReactiveHTML` components
:::

:link: ../how_to/custom_components/index.html#esm-components
:link-type: url

Deepen your understanding about custom ESM components, written in JavaScript, React, or AnyWidget.
:::

::::

## Architecture

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: architecture/comms
:link-type: doc

Deepen your understanding about how Panel communicates between Python and Javascript in different contexts.
:::

::::

## Styling

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: styling/design
:link-type: doc

Understand how the Panel `Design` and `Theme` components work internally.
:::

:link: styling/templates_overview
:link-type: doc

Discover Panel templates and how to use them.
:::

::::

## Dependencies

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: dependencies/param
:link-type: doc

Learn about why and how Panel utilizes the Param library.

```{image} https://assets.holoviz.org/panel/background/dependencies/param_logo_stacked.png
:width: 125px
:align: center
:name: Param
```

:::

:link: dependencies/bokeh
:link-type: doc

Learn about why and how Panel utilizes the Bokeh library.

```{image} https://assets.holoviz.org/panel/background/dependencies/bokeh-icon%405x.png
:width: 125px
:align: center
:name: Bokeh
```

:::

::::

## Technology comparisons

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: comparisons/compare_dash
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/comparisons/dash_logo.png
:width: 125px
:align: center
:name: Dash
```

:::

:link: comparisons/compare_ipywidgets
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/comparisons/jupyter_logo.png
:height: 125px
:align: center
:name: ipywidgets
```

:::

:link: comparisons/compare_voila
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/comparisons/voila_logo.webp
:width: 125px
:align: center
:name: Voila
```

:::

:link: comparisons/compare_streamlit
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/comparisons/streamlit_logo.png
:width: 125px
:align: center
:name: Streamlit
```

:::

:link: comparisons/compare_js
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/comparisons/JavaScript_logo.png
:width: 125px
:align: center
:name: JavaScript
```

:::

:link: comparisons/compare_bokeh
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/dependencies/bokeh-icon%405x.png
:width: 125px
:align: center
:name: Bokeh
```

:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

develop_seamlessly
apis
components
architecture
styling
dependencies
comparisons
```
