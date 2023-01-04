# Using Param with Panel

[Param](https://param.holoviz.org) is a library for handling all the user-modifiable parameters, arguments, and attributes that control your code. Panel is built on parameters, so to effectively learn to use Panel you should at least understand the basics about Param. Therefore we strongly recommend reading the first few sections of the [Param user guide](https://param.holoviz.org/user_guide/index.html).

Panel supports using parameters and dependencies between parameters as expressed by ``param`` in a simple way to encapsulate dashboards as declarative, self-contained classes.

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} Building UIs using Param
:link: uis
:link-type: doc

Discover how to generate UIs from Parameterized classes without writing any GUI related code.
:::

:::{grid-item-card} Declare Custom Widgets
:link: custom
:link-type: doc

Discover how to extend Param based UIs with custom widgets.
:::

:::{grid-item-card} Declare Parameter dependencies
:link: custom
:link-type: doc

Discover how to leverage `@param.depends` to express dependencies and trigger events based on UI interactions.
:::

:::{grid-item-card} Param subobjects
:link: subobjects
:link-type: doc

Discover how to structure Parameterized classes with subobjects to create nested UIs automatically.
:::

::::


```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

uis
custom
dependencies
subobjects
```