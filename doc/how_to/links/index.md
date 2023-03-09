# Link Parameters with Callbacks API

If you need full control over how your GUI is set up then you can manually define widgets that link directly to other objects using either Python or JavaScript (JS) callbacks. Python callbacks are simple for Python users to write and can directly access Python data structures, while JS callbacks can directly manipulate the displayed HTML document and allow setting up dynamic behavior even for exported HTML files (with no Python process running). This section contains how-to guides that address common tasks related the use of callbacks.

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} Create High-Level Python Links with `.link`
:link: links
:link-type: doc

How to use the convenient, high-level `.link` API to link parameters in Python.
:::

:::{grid-item-card} Create Low-Level Python Links with `.watch`
:link: watchers
:link-type: doc

How to use the flexible, low-level `.watch` API to trigger callbacks in Python.
:::

:::{grid-item-card} Link Two Objects in Javascript
:link: jslinks
:link-type: doc

How to link parameters of two objects in Javascript.
:::

:::{grid-item-card} Link Plot Parameters in Javascript
:link: link_plots
:link-type: doc

How to link Bokeh and HoloViews plot parameters in Javascript.
:::

:::{grid-item-card} Link Many Objects in Javascript
:link: jscallbacks
:link-type: doc

How to write arbitrary Javascript callbacks linking one or more objects.
:::

::::


```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

links
watchers
jslinks
link_plots
jscallbacks
```
