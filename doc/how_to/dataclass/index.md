# Interfacing with ipywidgets and Pydantic Models

Panel components and APIs are primarily built on [Param](https://param.holoviz.org/), a data-class-like library that adds parameter validation and event listeners to your objects.

When working with other frameworks like ipywidgets or Pydantic, which also provide dataclass-like objects, we offer various utilities to create Parameterized objects, `rx` expressions, and more for seamless integration with Panel.

::::{grid} 2 3 3 5
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`book;2.5em;sd-mr-1 sd-animate-grow50` Interact with ipywidgets
:link: ipywidget
:link-type: doc

How to interact with ipywidgets via familiar APIs like watch, bind, depends, and rx.
:::

:::{grid-item-card} {octicon}`triangle-up;2.5em;sd-mr-1 sd-animate-grow50` Interact with Pydantic models
:link: pydantic
:link-type: doc

How to interact with Pydantic Models via familiar APIs like watch, bind, depends, and rx.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

ipywidget
pydantic
```
