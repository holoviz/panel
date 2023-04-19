---
sd_hide_title: true
---

```{image} _static/logo_stacked.png
---
width: 125
---
```

<h2 style="margin-top: 0.3em;">A high-level app and dashboarding solution for Python</h2>

# Overview

## Featured Apps

::::{grid} 2 2 5 5
:gutter: 1

:::{grid-item-card} Attractors
:link: https://attractors.pyviz.demo.anaconda.com/attractors_panel
:link-type: url

```{image} https://assets.holoviews.org/panel/thumbnails/index/attractors.png
```
:::

:::{grid-item-card} Gapminders
:link: https://gapminders.pyviz.demo.anaconda.com
:link-type: url

```{image} https://assets.holoviews.org/panel/thumbnails/index/gapminders.png
```
:::

:::{grid-item-card} Penguins
:link: https://penguin-crossfilter.pyviz.demo.anaconda.com
:link-type: url

```{image} https://assets.holoviews.org/panel/thumbnails/index/penguins.png
```
:::

:::{grid-item-card} Glaciers
:link: https://glaciers.pyviz.demo.anaconda.com
:link-type: url

```{image} https://assets.holoviews.org/panel/thumbnails/index/glaciers.png
```
:::

:::{grid-item-card} Portfolio Optimizer
:link: https://portfolio-optimizer.pyviz.demo.anaconda.com
:link-type: url

```{image} https://assets.holoviews.org/panel/thumbnails/index/portfolio_optimizer.png
```
:::

::::

## Description

Panel is a Python library that makes it easy to create interactive dashboards and data apps using **the tools you already know and love**. With Panel, you can quickly prototype and iterate on apps and dashboards using your favorite editor or notebook environment. Unlike other tools, Panel supports a wide range of visualization libraries and development environments, which means you can choose the tools that work best for your workflow.

One of the most powerful features of Panel is its ability to handle large amounts of data and stream it directly to the frontend of your app. This allows you to build highly interactive and responsive apps that can handle real-time data updates with ease. Panel also provides deep bi-directional interactivity between the frontend and backend, which means you can build complex and interactive apps that respond to user input in real-time.

In addition to these core features, Panel provides a number of advanced features that make it a unique and powerful tool for building data apps and dashboards. For example, you can develop server-, pyodide-, and pyscript-backed applications, wrap your applications in polished templates for final deployment, and add authentication to your applications using the built-in OAuth providers.

Whether you're a domain expert, data scientist, software developer, or anyone in between, Panel provides a flexible and powerful platform for building interactive data apps and dashboards. With its broad range of features and support for multiple visualization libraries and development environments, Panel is a unique and powerful tool that can help you bring your data to life.

## Demo App

Simply drag the *slider* to see how the app responds to user input in real-time. To see how the app was built, check out the *Code* tab.

```{eval-rst}
.. notebook:: panel ../examples/homepage.ipynb
    :disable_interactivity_warning: True
```

The demo app is just a small example of what you can do with Panel. Whether you're building a simple dashboard or a complex data app, Panel makes it easy to create powerful and interactive user interfaces using the tools you already know and love. So why not give it a try and see what you can build with Panel today?

## Usage

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`rocket;2.5em;sd-mr-1` Core Concepts
:link: getting_started/core_concepts
:link-type: doc

Introduces you to some of the core concepts behind Panel, how to develop Panel applications effectively both in your IDE and in the notebook and some of the core features that make Panel such a powerful library.
:::

:::{grid-item-card} {octicon}`plug;2.5em;sd-mr-1` Installation
:link: getting_started/installation
:link-type: doc

Walks you through setting up your Python environment, installing Panel into it and how to configure your editor, IDE or notebook environment appropriately.
:::

:::{grid-item-card} {octicon}`tools;2.5em;sd-mr-1` Build an app
:link: getting_started/build_app
:link-type: doc

A more hands on tour taking you through the process of loading some data, displaying it and then building an application around it with some of the rich features that Panel supports.
:::

:::{grid-item-card} {octicon}`book;2.5em;sd-mr-1` How-to
:link: how_to/index
:link-type: doc

How-to guides provide step by step recipes for solving essential problems and tasks that arise during your work.
:::

::::

For usage questions or technical assistance, please head over to [Discourse](https://discourse.holoviz.org/). If you have any [issues](https://github.com/holoviz/panel/issues) or wish to [contribute code](https://help.github.com/articles/about-pull-requests), you can visit our [GitHub site](https://github.com/holoviz/panel).

## Useful Links

Project: [Source Repository](https://github.com/holoviz/panel) | [Issues & Ideas](https://github.com/holoviz/panel/issues) | [Q&A Support](https://discourse.holoviz.org/) | [Chat](https://discord.gg/rb6gPXbdAr)

Live Panel Environments: [Panelite](https://panelite.holoviz.org/) | [Panelite Repl](https://panelite.holoviz.org/repl/) | [Binder](https://mybinder.org/v2/gh/holoviz/panel/v0.14.4?urlpath=lab/tree/examples)

## HoloViz

Panel is a member of the ambitious [HoloViz](https://holoviz.org/) dataviz ecosystem and has first class support for the other members like [hvPlot](https://hvplot.holoviz.org) (simple .hvplot plotting api), [HoloViews](https://holoviews.org/) (powerful plotting api), and [Datashader](https://datashader.org/) (big data viz).

Panel is built on top of [Param](https://param.holoviz.org). Param enables you to annotate your code with parameter ranges, documentation, and dependencies between parameters and code. With this approach,

- you don't ever have to commit to whether your code will be used in a notebook, a data app, in batch processing, or reports.
- you will write less code and be able to develop large, maintainable code bases!

## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

::::{grid} 2

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://www.anaconda.com/
:link-type: url
:text-align: center
:columns: 3

```{image} https://static.bokeh.org/sponsor/anaconda.png
---
alt: Anaconda Logo
---
```
:::

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://www.blackstone.com/the-firm/
:link-type: url
:text-align: center
:columns: 3

```{image} https://static.bokeh.org/sponsor/blackstone.png
---
alt: Blackstone Logo
---
```
:::

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://numfocus.org/
:link-type: url
:text-align: center
:columns: 3

```{image} https://numfocus.org/wp-content/uploads/2017/03/numfocusweblogo_orig-1.png
---
alt: NumFOCUS Logo
---
```
:::

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://quansight.com/
:link-type: url
:text-align: center
:columns: 3

```{image} https://assets.holoviz.org/logos/Quansight-logo.svg
---
alt: Quansight Logo
---
```
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2
:caption: FOR USERS

getting_started/index
how_to/index
gallery/index
background/index
reference/index
api/index
FAQ
about/index
```

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2
:caption: FOR DEVELOPERS

developer_guide/index
```
