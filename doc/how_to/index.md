# How-to

The Panel How-to guides provide step by step recipes for solving essential problems and tasks that arise during your work. They assume that you've completed the Getting Started material and therefore already have some knowledge of how Panel works. There is no order to the guides, other than any potential prerequisites listed at the top of a page. Jump to the topic that is relevant to you now.


## Prepare to Develop

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`device-desktop;2.5em;sd-mr-1 sd-animate-grow50` Develop in a notebook or editor
:link: display/index
:link-type: doc

How to effectively develop apps in your favorite notebook or code editor environment.
:::

:::{grid-item-card} {octicon}`workflow;2.5em;sd-mr-1 sd-animate-grow50` Choose an API
:link: apis/index
:link-type: doc

How to choose from the different APIs offered by Panel.
:::

::::


## Build apps

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`rows;2.5em;sd-mr-1 sd-animate-grow50` Construct components
:link: components/index
:link-type: doc

How to construct and customize individual components like an image or slider widget.
:::

:::{grid-item-card} {octicon}`rows;2.5em;sd-mr-1 sd-animate-grow50` Bind widgets to functions (`Reactive API`)
:link: reactive/index
:link-type: doc

How to link selected widgets to arguments and make a reactive function.
:::

:::{grid-item-card} {octicon}`pulse;2.5em;sd-mr-1 sd-animate-grow50` Autogenerate UIs (`Interact API`)
:link: interact/index
:link-type: doc

How to autogenerate UIs for function arguments.
:::

:::{grid-item-card} {octicon}`codespaces;2.5em;sd-mr-1 sd-animate-grow50` Generate UIs from declared parameters (`Param API`)
:link: param/index
:link-type: doc

How to use Parameterized classes with Panel to generate UIs without writing GUI code.
:::

:::{grid-item-card} {octicon}`link;2.5em;sd-mr-1 sd-animate-grow50` Explicitly link parameters (`Callbacks API`)
:link: links/index
:link-type: doc

How to link the parameters of Panel components in Python and Javascript.
:::

::::


## Create specialized UIs

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`git-branch;2.5em;sd-mr-1 sd-animate-grow50` Build a sequential UI
:link: pipeline/index
:link-type: doc

How to build a Panel Pipeline that connects multiple panels into a sequential user interface.
:::

:::{grid-item-card} {octicon}`plus-circle;2.5em;sd-mr-1 sd-animate-grow50` Build custom components
:link: custom_components/index
:link-type: doc

How to extend Panel by building custom components.
:::

::::


## Manage session tasks

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1 sd-animate-grow50` Register session callbacks
:link: callbacks/index
:link-type: doc

How to set up callbacks on session related events (e.g. on page load or when a session is destroyed) and define periodic tasks.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1 sd-animate-grow50` Access session state
:link: state/index
:link-type: doc

How to access and manipulate state related to the user session, HTTP request and URL arguments.
:::

::::


## Test and debug

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`meter;2.5em;sd-mr-1 sd-animate-grow50` Enable profiling and debugging
:link: profiling/index
:link-type: doc

How to profile and debug your application using the admin dashboard and other tools.
:::

:::{grid-item-card} {octicon}`codescan-checkmark;2.5em;sd-mr-1 sd-animate-grow50` Set up testing for an application
:link: test/index
:link-type: doc

How to set up unit tests, UI tests and load testing to ensure your applications are (and stay) robust and scalable.
:::

::::


## Prepare to share

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`repo-template;2.5em;sd-mr-1 sd-animate-grow50` Apply templates
:link: templates/index
:link-type: doc

How to use a Template to customize the look and feel of a deployed Panel app.
:::

:::{grid-item-card} {octicon}`hourglass;2.5em;sd-mr-1 sd-animate-grow50` Improve performance
:link: performance/index
:link-type: doc

Discover some tips and tricks instructing you on how you can improve the performance of your application.
:::

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1 sd-animate-grow50` Cache data
:link: caching/index
:link-type: doc

How to cache data across sessions and memoize the output of functions.
:::

:::{grid-item-card} {octicon}`duplicate;2.5em;sd-mr-1 sd-animate-grow50` Improve scalability
:link: concurrency/index
:link-type: doc

How to improve the scalability of your Panel application.
:::

:::{grid-item-card} {octicon}`shield-check;2.5em;sd-mr-1 sd-animate-grow50` Add authentication
:link: authentication/index
:link-type: doc

How to configure OAuth to add authentication to a server deployment.
:::

::::

## Share your work

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`server;2.5em;sd-mr-1 sd-animate-grow50` Configure the server
:link: server/index
:link-type: doc

How to configure the Panel server.
:::

:::{grid-item-card} {octicon}`package-dependencies;2.5em;sd-mr-1 sd-animate-grow50` Integrate with other servers
:link: integrations/index
:link-type: doc

How to integrate Panel in other application based on Flask, FastAPI or Django.
:::

:::{grid-item-card} {octicon}`share;2.5em;sd-mr-1 sd-animate-grow50` Deploy applications
:link: deployment/index
:link-type: doc

How to deploy Panel applications to various cloud providers (e.g. Azure, GCP, AWS etc.)
:::

:::{grid-item-card} {octicon}`file;2.5em;sd-mr-1 sd-animate-grow50` Export apps
:link: export/index
:link-type: doc

How to export and save Panel applications as static files.
:::

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1 sd-animate-grow50` Run panel in WebAssembly
:link: wasm/index
:link-type: doc

How to run Panel applications entirely in the browser using WebAssembly (Wasm), Pyodide, and PyScript.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 1

prepare_to_develop
build_apps
create_specialized_uis
manage_session_tasks
test_and_debug
prepare_to_share
share_your_work
```
