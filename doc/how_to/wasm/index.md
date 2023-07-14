# Running Panel in the Browser with WASM

Panel lets you write dashboards and other applications in Python that are accessed using a web browser. Typically, the Python interpreter runs as a separate Jupyter or Bokeh server process, communicating with JavaScript code running in the client browser. However, **it is now possible to run Python directly in the browser**, with **no separate server needed!**

The underlying technology involved is called [WebAssembly](https://webassembly.org/) (or WASM). More specifically, [Pyodide](https://pyodide.org/) pioneered the ability to install Python libraries, manipulate the web page's [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction) from Python, and execute regular Python code entirely in the browser. A number of libraries have sprung up around Python in WASM, including [PyScript](https://pyscript.net/).

Panel can be run directly in Pyodide and has special support for rendering in PyScript.

This guide will take you through the process of either

- Automatically converting Panel applications into a Pyodide/PyScript based application
- Manually installing Panel in the browser and using it to render components.
- Embedding Panel in your Sphinx documentation.
- Setting up a Jupyterlite instance with support for Panel

::::{grid} 1 2 2 3
:gutter: 1 1 1 2

:::{grid-item-card} {octicon}`duplicate;2.5em;sd-mr-1 sd-animate-grow50` Convert to WASM.
:link: convert
:link-type: doc

Discover how to convert existing Panel applications to WebAssembly.
:::

:::{grid-item-card} {octicon}`code;2.5em;sd-mr-1 sd-animate-grow50` Use from WASM
:link: standalone
:link-type: doc

Discover how to set up and use Panel from Pyodide and PyScript.
:::

:::{grid-item-card} {octicon}`book;2.5em;sd-mr-1 sd-animate-grow50` Sphinx Integration
:link: sphinx
:link-type: doc

Discover how to integrate live Panel components in your Sphinx based documentation.
:::

:::{grid-item-card} {octicon}`zap;2.5em;sd-mr-1 sd-animate-grow50` JupyterLite
:link: jupyterlite
:link-type: doc

Discover how to set up a JupyterLite deployment capable of rendering interactive Panel output.
:::

::::

Note that since Panel is built on Bokeh server and Tornado it is also possible to implement your own authentication independent of the OAuth components shipped with Panel, [see the Bokeh documentation](https://docs.bokeh.org/en/latest/docs/user_guide/server.html#authentication) for further information.

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

convert
standalone
sphinx
jupyterlite
```
