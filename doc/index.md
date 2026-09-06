# Panel documentation

Panel is an [open-source](https://github.com/holoviz/panel/blob/main/LICENSE.txt) Python library for building data apps, from two widgets beside a plot in a notebook to a multi-page application served behind your own authentication. The same objects do both. A Panel component renders in Jupyter, JupyterLab, VS Code, Colab and marimo, and `panel serve` turns the file it lives in into an application without a rewrite.

Updates are declarative rather than script-level. You bind a function, or a component's state, to the widgets that feed it, and when one of those changes only what depends on it runs again, so an app that loads four million rows does not load them again because a slider moved. Panel renders what your plotting library already produces, whether that is Matplotlib, Plotly, Bokeh, HoloViews, Altair, ECharts, Deck.gl or an ipywidget, and the same app grows from a bound function into components made of components as it gets larger, which is refactoring rather than rewriting.

For a tour with runnable examples, see the [Panel home page](https://panel.holoviz.org/). This site is the documentation: guides, reference pages, and the API.

## Learn

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`rocket;2.5em;sd-mr-1` Getting started
:link: getting_started/index
:link-type: doc

Install Panel, build your first app, and get an overview of how its pieces fit together.
:::

:::{grid-item-card} {octicon}`mortar-board;2.5em;sd-mr-1` Tutorials
:link: tutorials/index
:link-type: doc

Guided, end-to-end walkthroughs that build a real application step by step.
:::

:::{grid-item-card} {octicon}`telescope;2.5em;sd-mr-1` Explanation
:link: explanation/index
:link-type: doc

Why Panel works the way it does: the reactive model, the two APIs, components, and design.
:::

::::

## Look something up

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`package;2.5em;sd-mr-1` Component gallery
:link: reference/index
:link-type: doc

Every component that ships with Panel, one page each, with the code that produced the example.
:::

:::{grid-item-card} {octicon}`beaker;2.5em;sd-mr-1` How-to guides
:link: how_to/index
:link-type: doc

Step-by-step recipes for the specific problems that come up: layout, auth, deployment, testing.
:::

:::{grid-item-card} {octicon}`book;2.5em;sd-mr-1` API reference
:link: api/index
:link-type: doc

The classes, parameters and methods that make up Panel's public interface.
:::

::::

## Also here

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Example apps
:link: gallery/index
:link-type: doc

Complete applications, each editable and runnable in the browser.
:::

:::{grid-item-card} {octicon}`versions;2.5em;sd-mr-1` Upgrade guide
:link: upgrade
:link-type: doc

What changed between major versions, and what to do about it.
:::

:::{grid-item-card} {octicon}`question;2.5em;sd-mr-1` FAQ
:link: FAQ
:link-type: doc

The questions that come up often enough to have a written answer.
:::

:::{grid-item-card} {octicon}`comment-discussion;2.5em;sd-mr-1` Community
:link: community
:link-type: doc

Where to ask, how to report a bug, and how to contribute.
:::

::::

For usage questions or technical assistance, head over to [Discourse](https://discourse.holoviz.org/) or our [Discord server](https://discord.gg/muhupDZM). If you have any [issues](https://github.com/holoviz/panel/issues), [feature requests](https://github.com/holoviz/panel/issues), or wish to [contribute](https://github.com/holoviz/panel/blob/main/CONTRIBUTING.MD), you can visit our [GitHub site](https://github.com/holoviz/panel).

## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

::::{grid} 2 2 2 4

:::{grid-item-card}
:class-body: sponsor-logo
:link: https://www.anaconda.com/
:link-type: url
:text-align: center

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
tutorials/index
explanation/index
reference/index
how_to/index
gallery/index
api/index
community
upgrade
FAQ
about/index
```

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2
:caption: FOR DEVELOPERS

Developer Guide <developer_guide/index>
```
