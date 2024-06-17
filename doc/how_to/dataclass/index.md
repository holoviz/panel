# Interfacing with ipywidget and pydantic models

Panel components and APIs primarily build on [Param](https://param.holoviz.org/), a library to add parameter validation and event listeners to your objects. This means that when working with other frameworks like ipywidgets, which is traitlets based, or Pydantic, which also provides dataclass-like objects you have to use their APIs. In order to better integrate these tools in your Panel applications we provide a variety of utilities to create Parameterized objects, `rx` expressions and much more from models implemented by these other libraries.

::::{grid} 2 3 3 5
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`paper-airplane;2.5em;sd-mr-1 sd-animate-grow50` Interact with ipywidgets
:link: ipy
:link-type: doc

How to interact with ipywidgets via familiar APIs like watch, bind, depends, and rx.
:::

:::{grid-item-card} {octicon}`paper-airplane;2.5em;sd-mr-1 sd-animate-grow50` Interact with Pydantic models
:link: dataclass/pydantic
:link-type: doc

How to interact with Pydantic Models via familiar APIs like watch, bind, depends, and rx.
:::

::::

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

ipywidgets
pydantic
```
