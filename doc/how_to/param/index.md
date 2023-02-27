# Declare UIs with `Param` API

Panel is built on [Param](https://param.holoviz.org) - a library for handling all the user-modifiable parameters, arguments, and attributes that control your code. This section contains how-to guides for using `Param` objects and declared dependencies to generate user interfaces with Panel.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Generate Widgets from `Parameters`
:link: uis
:link-type: doc

How to generate UIs from Parameterized classes without writing any GUI related code.
:::

:::{grid-item-card} Declare Custom Widgets
:link: custom
:link-type: doc

How to extend Param based UIs with custom widgets.
:::

:::{grid-item-card} Declare Parameter dependencies
:link: dependencies
:link-type: doc

How to leverage `@param.depends` to express dependencies and trigger events based on UI interactions.
:::

:::{grid-item-card} Create nested UIs
:link: subobjects
:link-type: doc

How to structure Parameterized classes with subobjects to create nested UIs automatically.
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
