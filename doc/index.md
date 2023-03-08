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

Panel is an [open-source](https://github.com/holoviz/panel/blob/main/LICENSE.txt) Python library that lets you create custom interactive web apps and dashboards by connecting user-defined widgets to plots, images, tables, or text.

```{eval-rst}
.. notebook:: panel ../examples/homepage.ipynb
    :disable_interactivity_warning: True
```

Compared to other approaches, Panel is novel in that it supports nearly all plotting libraries, works just as well in a Jupyter notebook as on a standalone secure web server, uses the same code for both those cases, supports both Python-backed and static HTML/JavaScript exported applications, and can be used to develop rich interactive applications without tying your domain-specific code to any particular GUI or web tools.

Panel makes it simple to:

- Use the PyData tools and plotting libraries that you know and love
- Develop in your favorite editor or notebook environment and seamlessly deploy the resulting application
- Iterate quickly to prototype apps and dashboards while offering polished templates for your final deployment
- Support deep interactivity by communicating client-side interactions and events to Python
- Stream data large and small to the frontend
- Add authentication to your application using the inbuilt OAuth providers

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

:::{grid-item-card} {octicon}`book;2.5em;sd-mr-1` User Guide
:link: user_guide/index
:link-type: doc

For a more in-depth guide through a range of topics, starting from the various APIs of Panel, through to building custom components and authentication visit our user guide.
:::

::::

For usage questions or technical assistance, please head over to [Discourse](https://discourse.holoviz.org/). If you have any [issues](https://github.com/holoviz/panel/issues) or wish to [contribute code](https://help.github.com/articles/about-pull-requests), you can visit our [GitHub site](https://github.com/holoviz/panel).

## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

::::{grid} 2

:::{grid-item-card}
:link: https://www.anaconda.com/
:link-type: url
:text-align: center
:columns: 6

```{image} https://static.bokeh.org/sponsor/anaconda.png
---
alt: Anaconda Logo
---
```
:::


:::{grid-item-card}
:link: https://www.blackstone.com/the-firm/
:link-type: url
:text-align: center
:columns: 6

```{image} https://static.bokeh.org/sponsor/blackstone.png
---
alt: Blackstone Logo
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
about/index.rst
```

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2
:caption: FOR DEVELOPERS

developer_guide/index
releases
```
