# APIs

Panel can be used to make a simple app in minutes, but you can also create complex apps with fully customized behavior and appearance or even flexibly integrate GUI support into long-term, large-scale software projects.

To accommodate these different ways of using Panel, multiple APIs are available. Nearly all of the functionality of Panel can be accessed using any of the APIs, but each makes certain things much easier than others.

Let's go work through each API with an example app while pointing out the benefits and drawback along the way. Here's a quick summary:
1. The ``Reactive API`` approach allows you to define a reactive function that is bound directly to a set of widgets using `pn.bind`. This API is efficient while still being explicit, flexible, and maintainable. We recommend this for most users, especially those that are new to Panel.
2.  When writing libraries or other code that might be used independently of the actual GUI, a Parameterized class can be a great way to organize the code. In this case, dive into the ``Declarative API``.
3. If you need low-level control or want to complement any of the other approaches, defining explicit callbacks can be done with the ``Callbacks API``.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`infinity;2.5em;sd-mr-1 sd-animate-grow50` 1. Reactive API
:link: reactive
:link-type: doc

Linking functions or methods to widgets using ``pn.bind`` or the equivalent ``pn.depends`` decorator.
:::

:::{grid-item-card} {octicon}`codespaces;2.5em;sd-mr-1 sd-animate-grow50` 2. Declarative API
:link: parameterized
:link-type: doc

Declare parameters and their ranges in `Parameterized` classes, then get GUIs (and value checking!) for free.
:::

:::{grid-item-card} {octicon}`link;2.5em;sd-mr-1 sd-animate-grow50` 3. Callbacks API
:link: callbacks
:link-type: doc

Generate a UI by manually declaring callbacks that update panels or panes.
:::

::::

## Examples

Below are additional recipes using each API to create slightly more advanced apps.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Stock Explorer - Callback API
:img-top: https://assets.holoviz.org/panel/how_to/apis/stocks_callback.png
:link: examples/stocks_callbacks
:link-type: doc

Build a stock explorer app using the `.param.watch` callback API.
:::

:::{grid-item-card} Stock Explorer - Declarative API
:img-top: https://assets.holoviz.org/panel/how_to/apis/stocks_declarative.png
:link: examples/stocks_declarative
:link-type: doc

Build a stock explorer app using the Param based declarative API.
:::

:::{grid-item-card} Stock Explorer - Reactive API
:img-top: https://assets.holoviz.org/panel/how_to/apis/stocks_reactive.png
:link: examples/stocks_reactive
:link-type: doc

Build a stock explorer app using the reactive API.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

reactive
interact
parameterized
callbacks
```
