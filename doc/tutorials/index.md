# Tutorials

These tutorials provides you with **a structured and step-by-step learning path** to **go from Zero to Hero**.

Each guide gradually builds on the previous ones, but it's structured to separate topics, so that you can go directly to a specific topic of interest and start learning.

We will assume you have successfully been able to [install Panel](../getting_started/installation.md) as described in the [Getting Started Guide](../getting_started/index.md). If not please reach out for help on [Discord](https://discord.gg/rb6gPXbdAr).

---

## Basic

These tutorials are for you that is just starting to discover Panel.

You will learn to develop and deploy amazing tools and apps that can be contained within a single Python file or notebook.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Serve Apps
:link: beginner/serve
:link-type: doc

Learn how to serve apps from a single Python script, Notebook or Markdown document.
:::

:::{grid-item-card} {octicon}`dependabot;2.5em;sd-mr-1` Build a Chat Bot
:link: beginner/build_chatbot
:link-type: doc

Learn how to build a simple *chat bot*.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Develop in a Notebook
:link: beginner/develop_notebook
:link-type: doc

Learn the basic techniques for developing Panel apps efficiently in a notebook.
:::

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Develop in an Editor
:link: beginner/develop_editor
:link-type: doc

Learn the basic techniques for developing Panel apps efficiently in an editor.
:::

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Display objects with `pn.panel`
:link: beginner/pn_panel
:link-type: doc

Learn how to display Python objects easily and dynamically with `pn.panel`.
:::

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Display objects with Panes
:link: beginner/panes
:link-type: doc

Learn how to display Python objects efficiently and specifically with Panes.
:::

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Layout Objects
:link: beginner/layouts
:link-type: doc

Learn how to layout Python objects including Panel components
:::

:::{grid-item-card} {octicon}`person;2.5em;sd-mr-1` Accept User Input
:link: beginner/widgets
:link-type: doc

Learn how to accept user input with widgets.
:::

:::{grid-item-card} {octicon}`plug;2.5em;sd-mr-1` Param
:link: param
:link-type: doc

Panel and other projects in the HoloViz ecosystem all build on Param. In this section you will learn the basic concepts behind Param that you need to know to become an effective user of Panel.
:::

:::{grid-item-card} {octicon}`pulse;2.5em;sd-mr-1` Interactivity
:link: interactivity
:link-type: doc

In this section you learn how to leverage Parameters and dependencies on parameters to add interactivity. In particular we will focus on implementing interactivity through reactivity, rather than the more imperative style of programming you might be used to from other UI frameworks.
:::

:::{grid-item-card} {octicon}`rows;2.5em;sd-mr-1` Layouts
:link: layouts
:link-type: doc

In this section we will discover how layouts and sizing works in Panel, taking you through the difference between inherent sizing, fixed sizing and responsive sizing and then cover responsive layouts.
:::

:::{grid-item-card} {octicon}`paintbrush;2.5em;sd-mr-1` Styling
:link: styling
:link-type: doc

In this section we will review different approaches for styling components, from applying `Design` components, through applying `stylesheets` and `css_classes`.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

beginner/serve
beginner/build_chatbot
beginner/develop_notebook
beginner/develop_editor
beginner/pn_panel
beginner/panes
beginner/layouts
beginner/widgets
param
interactivity
layouts
styling
```

---

## Intermediate

These tutorials are for you that is ready to navigate and explore more advanced features of Panel.

You will learn to develop and deploy complex tools and multi-page apps that can support more demanding use cases.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Serve Panel Apps
:link: intermediate/serve
:link-type: doc

Learn to serve multi-page apps and how-to customize the Panel server.
:::

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Develop in an Editor
:link: intermediate/develop_editor
:link-type: doc

Learn how to debug applications in an Editor
:::

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Structure with DataStore
:link: intermediate/structure_data_store
:link-type: doc

Learn how to structure larger applications with the `DataStore` pattern
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

intermediate/serve
intermediate/develop_editor
intermediate/structure_data_store
```

---

## Advanced

These tutorials are for you that that is ready to pioneer and push the boundaries of what can be achieved with Panel.

You will learn how to customize and extend Panel to support your domain or specialized use cases.
