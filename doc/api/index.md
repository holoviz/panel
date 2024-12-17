# API Reference

The Panel API Reference Manual provides a comprehensive reference for
all methods and parameters on Panel components. For more information
on how to use the components see the [Component Gallery](../reference/index).

## Overview

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`workflow;2.5em;sd-mr-1` Cheat Sheet
:link: cheatsheet
:link-type: doc

The Cheat Sheet provides a high-level overview of some of the most important functions in Panel.
:::

:::{grid-item-card} {octicon}`codespaces;2.5em;sd-mr-1` Config
:link: config
:link-type: doc

The `panel.config` provides a way to set high-level configuration options.
:::

:::{grid-item-card} {octicon}`link;2.5em;sd-mr-1` State
:link: state
:link-type: doc

The `panel.state` object holds session state and provide various methods to attach events and tasks to a session.
:::

::::

## Module Structure

[`panel.io`](panel.io)
: Utilities for working with Panel components

[`panel.layout`](panel.layout)
: Panel layout components

[`panel.pane`](panel.pane)
: Panel layout components

[`panel.param`](panel.param)
: Components for integration with the param library

[`panel.pipeline`](panel.pipeline)
: Panel Pipeline component

[`panel.widgets`](panel.widgets)
: Widget components

[`panel.viewable`](panel.viewable)
: Baseclasses for all Panel components

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

cheatsheet
config
state
panel.io
panel.layout
panel.pane
panel.param
panel.pipeline
panel.template
panel.util
panel.viewable
panel.widgets
```
