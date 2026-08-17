# How-to

The Panel How-to guides provide step by step recipes for solving essential problems and tasks that arise during your work. They assume that you've completed the Getting Started material and therefore already have some knowledge of how Panel works. There is no order to the guides, other than any potential prerequisites listed at the top of a page. Jump to the topic that is relevant to you now.

## Develop Efficiently

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: notebook/index
:link-type: doc

How to effectively develop apps in a notebook environment.
:::

:link: editor/index
:link-type: doc

How to effectively develop apps in a Python or Markdown file.
:::

::::

## Build apps

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: components/index
:link-type: doc

How to construct and customize individual components like an image or slider widget.
:::

:link: layout/index
:link-type: doc

How to arrange and size components on the page.
:::

:link: styling/index
:link-type: doc

How to apply designs, themes and custom styling to components to achieve a polished look and feel.
:::

:link: interactivity/index
:link-type: doc

How to link add interactivity to your applications using reactive APIs.
:::

:link: templates/index
:link-type: doc

How to use a Template to customize the look and feel of a deployed Panel app.
:::

::::

## Use specialized UIs and APIs

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: pipeline/index
:link-type: doc

How to build a Panel Pipeline that connects multiple panels into a sequential user interface.
:::

:link: custom_components/index
:link-type: doc

How to extend Panel by building custom components.
:::

:link: param/index
:link-type: doc

How to use Parameterized classes with Panel to generate UIs without writing GUI code.
:::

:link: links/index
:link-type: doc

How to link the parameters of Panel components in Python and Javascript.
:::

::::

## Manage session tasks

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: callbacks/index
:link-type: doc

How to set up callbacks on session related events (e.g. on page load or when a session is destroyed) and define periodic tasks.
:::

:link: state/index
:link-type: doc

How to access and manipulate state related to the user session, HTTP request and URL arguments.
:::

::::

## Extending Panel

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: custom_components/index
:link-type: doc

How to create custom components including widgets, layouts and panes using pure-Python, JS or React.
:::

::::

## Test and debug

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: profiling/index
:link-type: doc

How to profile and debug your application using the admin dashboard and other tools.
:::

:link: test/index
:link-type: doc

How to set up unit tests, UI tests and load testing to ensure your applications are (and stay) robust and scalable.
:::

:link: logging/index
:link-type: doc

How to configure the logging level and format
:::

::::

## Prepare to share

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: performance/index
:link-type: doc

Discover some tips and tricks instructing you on how you can improve the performance of your application.
:::

:link: caching/index
:link-type: doc

How to cache data across sessions and memoize the output of functions.
:::

:link: concurrency/index
:link-type: doc

How to improve the scalability of your Panel application.
:::

:link: best_practices/index
:link-type: doc

A checklist of best practices for improving the development and user experience with Panel.
:::

:link: authentication/index
:link-type: doc

How to configure OAuth to add authentication to a server deployment.
:::

::::

## Share your work

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: server/index
:link-type: doc

How to configure the Panel server.
:::

:link: distribute/index
:link-type: doc

How to distribute your Panel applications
:::

:link: integrations/index
:link-type: doc

How to integrate Panel in other application based on Flask, FastAPI or Django.
:::

:link: deployment/index
:link-type: doc

How to deploy Panel applications to various cloud providers (e.g. Azure, GCP, AWS etc.)
:::

:link: export/index
:link-type: doc

How to export and save Panel applications as static files.
:::

:link: wasm/index
:link-type: doc

How to run Panel applications entirely in the browser using WebAssembly (Wasm), Pyodide, and PyScript.
:::

:link: desktop_or_mobile/index
:link-type: doc

How to convert Panel applications into standalone desktop or mobile applications.
:::

::::

## Migrate to Panel

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: streamlit_migration/index
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/comparisons/streamlit_logo.png
:width: 125px
:align: center
:name: Streamlit
```

How to migrate existing Streamlit applications to Panel.
:::

:link: migrate/anywidget/index
:link-type: doc

```{image} https://assets.holoviz.org/panel/background/comparisons/anywidget_logo.png
:width: 125px
:align: center
:name: AnyWidget
```

How to convert AnyWidget widgets to Panel widgets.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 1

prepare_to_develop
build_apps
use_specialized_uis
manage_session_tasks
extending_panel
test_and_debug
prepare_to_share
share_your_work
migrate_to_panel
```
