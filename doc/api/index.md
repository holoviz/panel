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


-------

## Module Structure

[`panel.auth`](panel.auth)
: Module containing authentication handlers.

[`panel.chat`](panel.chat)
: Subpackage containing Panel Chat components

[`panel.command`](panel.chat)
: Subpackage containing Panel CLI commands

[`panel.compiler`](panel.compiler)
: Utilities for bundling and compiling external JS and CSS resources.

[`panel.config`](panel.config)
: Module containing Panel config and extension objects.

[`panel.custom`](panel.custom)
: Baseclasses for creating custom components.

[`panel.depends`](panel.depends)
: Module exposing `param.bind` and `param.depends`.

[`panel.interact`](panel.interact)
: Module implementing the `interact` API.

[`panel.io`](panel.io)
: Subpackage containing all IO related functionality.

[`panel.layout`](panel.layout)
: Subpackage containing layout components

[`panel.links`](panel.links)
: Module containing implementation responsible Javascript linking and callbacks.

[`panel.models`](panel.models)
: Subpackage containing Bokeh model implementations of custom components.

[`panel.pane`](panel.pane)
: Subpackage containing `Pane` components.

[`panel.param`](panel.param)
: Module implementing components for integration with the param library.

[`panel.pipeline`](panel.pipeline)
: Module containing the `Pipeline` component.

[`panel.reactive`](panel.reactive)
: Module containing baseclasses for Panel components with reactive APIs.

[`panel.template`](panel.template)
: Subpackage containing implementations for `Template` components.

[`panel.theme`](panel.theme)
: Subpackage implementing `Design` and `Theme` components.

[`panel.util`](panel.util)
: Subpackage containing generic utilities.

[`panel.viewable`](panel.viewable)
: Module containing baseclasses for all Panel components.

[`panel.widgets`](panel.widgets)
: Subpackage containing `Widget` components.

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

cheatsheet
config
state
panel.auth
panel.chat
panel.command
panel.compiler
panel.config
panel.custom
panel.depends
panel.io
panel.layout
panel.links
panel.models
panel.pane
panel.param
panel.pipeline
panel.reactive
panel.template
panel.theme
panel.util
panel.viewable
panel.widgets
```
