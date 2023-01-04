# Linking parameters

In the [Param how-to guide](../param/index), we have seen how Parameterized classes can be used to automatically generate a graphical user interface for Python code without any additional effort. If you need full control over how your GUI is set up, you can instead manually define widgets linking directly to other objects using either Python or JavaScript (JS) callbacks. Python callbacks are simple for Python users to write and can directly access Python data structures, while JS callbacks can directly manipulate the displayed HTML document and allow setting up dynamic behavior even for exported HTML files (with no Python process running).

Here we will show how to link parameters of Panel objects, typically from widgets to other objects. To do this, we will introduce three API calls:

* ``obj.link``: 
* ``obj.param.watch``: 
* ``obj.jslink``: high-level API to link objects via JS code
* ``obj.jscallback``: a lower-level API to define arbitrary Javascript callbacks

::::{grid} 1 2 2 4
:gutter: 1 1 1 2

:::{grid-item-card} Watchers
:link: watchers
:link-type: doc

Discover how to use the powerful but low-level `.param.watch` API provided by [param](https://param.pyviz.org) to trigger callbacks on parameters.
:::

:::{grid-item-card} Links in Python
:link: links
:link-type: doc

Discover how to use the convenient, high-level `.link` API to link parameters in Python.
:::

:::{grid-item-card} Links in Javascript
:link: jslinks
:link-type: doc

Discover how to use the convenient, high-level `.jslink` API to link parameters in Javascript.
:::

:::{grid-item-card} Link plots in Javascript
:link: jslinks
:link-type: doc

Discover how to use `.jslink` to link Bokeh and HoloViews plot parameters in Javascript.
:::

:::{grid-item-card} Javascript callbacks
:link: jscallbacks
:link-type: doc

Discover how to use the `.jscallback` API to write arbitrary JS callbacks linking one or more components.
:::

::::


```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

watchers
links
jslinks
link_plots
jscallback
```