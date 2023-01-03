# How-to Guide

The Panel's How to Guides provide step by step recipes for solving essential problems and tasks. They are more advanced than the Getting Started material and assume some knowledge of how Panel works.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Session callbacks and events
:link: callbacks/index
:link-type: doc

How to set up callbacks on session related events and periodic tasks.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Accessing session state
:link: state/index
:link-type: doc

How to access state related to the user session, HTTP request and URL arguments.
:::

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1` Caching
:link: caching/index
:link-type: doc

How to cache data across sessions and memoize the output of functions.
:::

:::{grid-item-card} {octicon}`device-desktop;2.5em;sd-mr-1` Display and Preview output
:link: display/index
:link-type: doc

How to display Panel components and apps in your favorite notebook or editor environment.
:::

:::{grid-item-card} {octicon}`file;2.5em;sd-mr-1` Exporting and Saving output
:link: export/index
:link-type: doc

How to export and save Panel applications as static files.
:::

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Running in WebAssembly
:link: wasm/index
:link-type: doc

How to run Panel applications entirely in the browser using WebAssembly, Pyodide and PyScript.
:::

:::{grid-item-card} {octicon}`server;2.5em;sd-mr-1` Server Configuration
:link: server/index
:link-type: doc

How to configure the Panel server.
:::

:::{grid-item-card} {octicon}`package-dependencies;2.5em;sd-mr-1` Server Integrations
:link: integrations/index
:link-type: doc

How to integrate Panel in other application based on Flask, FastAPI or Django.
:::

:::{grid-item-card} {octicon}`share;2.5em;sd-mr-1` Deploying applications
:link: deployment/index
:link-type: doc

How to deploy Panel applications to various cloud providers (e.g. Azure, GCP, AWS etc.)
:::

:::{grid-item-card} {octicon}`shield-check;2.5em;sd-mr-1` Authentication
:link: authentication/index
:link-type: doc

How to configure OAuth to add authentication to a server deployment.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

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
