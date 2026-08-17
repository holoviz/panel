# Declare UIs with Declarative API

Panel is built on [Param](https://param.holoviz.org) - a library for handling all the user-modifiable parameters, arguments, and attributes that control your code. This section contains how-to guides for using `Param` objects and declared dependencies to generate user interfaces with Panel.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:link: uis
:link-type: doc

How to generate UIs from Parameterized classes without writing any GUI related code.
:::

:link: custom
:link-type: doc

How to extend Param based UIs with custom widgets.
:::

:link: dependencies
:link-type: doc

How to leverage `@param.depends` to express dependencies and trigger events based on UI interactions.
:::

:link: subobjects
:link-type: doc

How to structure Parameterized classes with subobjects to create nested UIs automatically.
:::

::::

## Examples

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:img-top: https://assets.holoviz.org/panel/how_to/param/action_button.png
:link: examples/action_button
:link-type: doc

Using `param.Action` to define a UI with a button.
:::

:img-top: https://assets.holoviz.org/panel/how_to/param/loading.png
:link: examples/loading
:link-type: doc

Automatically enable a loading indicator for components rendered dynamically.
:::

:img-top: https://assets.holoviz.org/panel/how_to/param/subobjects.png
:link: examples/subobjects
:link-type: doc

Using Param to express a nested UI using a hierarchy of classes.
:::

:img-top: https://assets.holoviz.org/panel/how_to/param/precedence.png
:link: examples/precedence
:link-type: doc

Using Parameter precedence to control the visibility of components.
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
