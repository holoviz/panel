# How-to Guide

The Panel's How to Guides provide step by step recipes for solving essential problems and tasks. They are more advanced than the Getting Started material and assume some knowledge of how Panel works.

## Basics

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`workflow;2.5em;sd-mr-1` Choose an API
:link: apis/index
:link-type: doc

Discover the different APIs offered by Panel and how to choose between them.
:::

:::{grid-item-card} {octicon}`codespaces;2.5em;sd-mr-1` Declaring UIs with parameters
:link: param/index
:link-type: doc

Discover how to use Parameters with Panel.
:::

:::{grid-item-card} {octicon}`link;2.5em;sd-mr-1` Link Parameters
:link: links/index
:link-type: doc

Discover different ways of linking parameters in Python and Javascript.
:::

::::


## Advanced

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Session callbacks and events
:link: callbacks/index
:link-type: doc

How to set up callbacks on session related events and periodic tasks.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Access Session State
:link: state/index
:link-type: doc

How to access state related to the user session, HTTP request and URL arguments.
:::

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1` Cache Data
:link: caching/index
:link-type: doc

How to cache data across sessions and memoize the output of functions.
:::

::::


## Display and Export

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`device-desktop;2.5em;sd-mr-1` Display and Preview Output
:link: display/index
:link-type: doc

How to display Panel components and apps in your favorite notebook or editor environment.
:::

:::{grid-item-card} {octicon}`file;2.5em;sd-mr-1` Export and Save Output
:link: export/index
:link-type: doc

How to export and save Panel applications as static files.
:::

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Run Panel in WebAssembly
:link: wasm/index
:link-type: doc

How to run Panel applications entirely in the browser using WebAssembly, Pyodide and PyScript.
:::

::::


## Server configuration and deployment

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`server;2.5em;sd-mr-1` Configure the Server
:link: server/index
:link-type: doc

How to configure the Panel server.
:::

:::{grid-item-card} {octicon}`package-dependencies;2.5em;sd-mr-1` Integrate with other Servers
:link: integrations/index
:link-type: doc

How to integrate Panel in other application based on Flask, FastAPI or Django.
:::

:::{grid-item-card} {octicon}`share;2.5em;sd-mr-1` Deploy Applications
:link: deployment/index
:link-type: doc

How to deploy Panel applications to various cloud providers (e.g. Azure, GCP, AWS etc.)
:::

:::{grid-item-card} {octicon}`shield-check;2.5em;sd-mr-1` Add Authentication
:link: authentication/index
:link-type: doc

How to configure OAuth to add authentication to a server deployment.
:::

::::


```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

apis/index
param/index
links/index
callbacks/index
state/index
caching/index
export/index
wasm/index
server/index
integrations/index
deployment/index
authentication/index
```
