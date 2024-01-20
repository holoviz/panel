# Tutorial

The tutorial provides you with **a structured and step-by-step guide on how to use Panel effectively**.

Each section gradually builds on the previous ones, but it's structured to separate topics, so that you can go directly to a specific topic of interest and start learning.

We will assume you have successfully been able to [install Panel](../getting_started/installation.md) as described in the [Getting Started Guide](../getting_started/index.md). If not please reach out for help on [Discord](https://discord.gg/rb6gPXbdAr).

---

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Serve Panel Apps
:link: panel_serve
:link-type: doc

Learn how to serve your Panel apps using the `panel serve` command.
:::

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Develop in an Editor
:link: develop_editor
:link-type: doc

Learn how to develop Panel components, tools and apps efficiently in an editor.
:::

:::{grid-item-card} {octicon}`note;2.5em;sd-mr-1` Develop in a Notebook
:link: develop_editor
:link-type: doc

Learn how to develop Panel components, tools and apps efficiently in a notebook.
:::

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1` Display objects easily with `pn.panel`
:link: display_pn_panel
:link-type: doc

Learn how to display objects easily and flexibly with `pn.panel`.
:::

:::{grid-item-card} {octicon}`plug;2.5em;sd-mr-1` Param
:link: param
:link-type: doc

Panel and other projects in the HoloViz ecosystem all build on Param. In this section you will learn the basic concepts behind Param that you need to know to become an effective user of Panel.
:::

:::{grid-item-card} {octicon}`container;2.5em;sd-mr-1` Components
:link: components
:link-type: doc

Panel is a library that provides a lot of object types and while building an app, even a simple one, you will create and interact with many of them. In this section you will get a high-level overview of the different component types Panel offers and how to use them.
:::

:::{grid-item-card} {octicon}`pulse;2.5em;sd-mr-1` Interactivity
:link: interactivity
:link-type: doc

In this section you learn how to leverage Parameters and dependencies on parameters to add interactivity. In particular we will focus on implementing interactivity through reactivity, rather than the more imperative style of programming you might be used to from other UI frameworks.
:::

:::{grid-item-card} {octicon}`browser;2.5em;sd-mr-1` Effective Development
:link: development
:link-type: doc

In this section we will introduce you to the most important concepts you need to know to become an effective Panel developer in notebooks and your favorite editor.
:::

:::{grid-item-card} {octicon}`rows;2.5em;sd-mr-1` Layouts
:link: layouts
:link-type: doc

In this section we will discover how layouts and sizing works in Panel, taking you through the difference between inherent sizing, fixed sizing and responsive sizing and then cover responsive layouts.
:::

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1` Structuring Applications
:link: structure
:link-type: doc

In this section we will take you through the process of structuring a more complex application, discussing different approaches for managing reactivity and how to create a composable architecture for your applications.
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

panel_serve
develop_editor
develop_notebook
display_pn_panel
param
components
interactivity
development
layouts
structure
styling
```
