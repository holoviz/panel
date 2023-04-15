---
sd_hide_title: true
---

```{image} _static/logo_stacked.png
---
width: 125
---
```

# Overview

<h2 style="margin-top: 0.3em;">A high-level app and dashboarding solution for Python</h2>

Panel is an [open-source and free](https://github.com/holoviz/panel/blob/main/LICENSE.txt) Python library that lets you create interactive tools, dashboards and data apps by connecting user-defined widgets to plots, images, tables, text and more.

```{eval-rst}
.. notebook:: panel ../examples/homepage.ipynb
    :disable_interactivity_warning: True
```

Compared to other approaches, Panel is novel in the number of visualization libraries, development environments and deployment options that it supports.

Panel makes it simple to:

- Use the PyData tools and visualization libraries that you know and love
- Develop in your favorite editor or notebook environment
- Iterate quickly to prototype apps and dashboards
- Support deep bi-directional interactivity between the frontend and the backend
- Stream data large and small to the frontend
- Test and maintain your applications
- Develop server-, pyodide- and pyscript-backed applications
- Wrap your applications in polished templates for your final deployment
- Add authentication to your applications using the inbuilt OAuth providers

## Useful Links

Project: [Source Repository](https://github.com/holoviz/panel) | [Issues & Ideas](https://github.com/holoviz/panel/issues) | [Q&A Support](https://discourse.holoviz.org/) | [Chat](https://discord.gg/rb6gPXbdAr)

Live Environments: [Panelite](https://panelite.holoviz.org/) | [Panelite Repl](https://panelite.holoviz.org/repl/) | [Binder](https://mybinder.org/v2/gh/holoviz/panel/v0.14.4?urlpath=lab/tree/examples)

## Demo Apps

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
