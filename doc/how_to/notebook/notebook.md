# Display Output in Notebooks

This guide addresses how to display output in Jupyter and non-Jupyter based notebook environments.

---

Once you have installed Panel it should automatically set up Jupyter notebook and JupyterLab extensions for rendering Panel output and configuring communication channels to ensure the rendered output syncs bi-directionally with the Python process.

Panel supports **JupyterLab 4.4–4.6** with `pyviz_comms >= 3.0.2`. See the [JupyterLab support matrix](jupyterlab_support) for the full version table.

Recommended install for JupyterLab:

```bash
pip install "panel[jupyter]"
```

## Run Panel in another notebook kernel

You generally have two ways to install JupyterLab/Jupyter Notebook:

1. directly in your working environment that contains all the dependencies you need to run your project
2. in another environment, maybe a central environment or an environment dedicated to Jupyter, in which case when you run a notebook you should pick the kernel of your project environment

When in the second setup, you need to ensure that `pyviz_comms >= 3.0.2` is explicitly installed in the same environment as JupyterLab/Jupyter Notebook (with `conda install "pyviz_comms>=3.0.2"` or `pip install "pyviz-comms>=3.0.2"`) for bi-directional communication to be fully working.

## Loading the extension

The first step when working in a notebook environment should always be to load the `panel.extension`:

```{pyodide}
import panel as pn

pn.extension()
```

The extension ensures that all required Javascript and CSS resources are added to your notebook environment. If you are going to be using any custom extensions, such as [Vega](../../reference/panes/Vega) or [Tabulator](../../reference/widgets/Tabulator) you must ensure that you initialize these as well:

```{pyodide}
pn.extension('vega', 'tabulator')
```

## Display output

One of the major benefits of notebook environments is that they support rich output. This means that if you place an object with rich output at the end of a cell the notebook will figure out how to render the rich representation. Panel uses this mechanism to ensure that all components return a rich representation:

```{pyodide}
pane = pn.panel('<marquee>Here is some custom HTML</marquee>')

pane
```

To instead see a textual representation of the component, you can use the `print` function on any Panel object:

```{pyodide}
print(pane)
```

### The ``display`` function

:::{attention}
The `display` function is an IPython built-in and will only work in notebooks.
:::

To avoid having to put a Panel on the last line of a notebook cell, e.g. to display it from inside a function call, you can use the IPython built-in ``display`` function:

```{pyodide}
def display_marquee(text):
    display(pn.panel('<marquee>{text}</marquee>'.format(text=text)))

display_marquee('This Panel was displayed from within a function')
```

## Render as ipywidget

While Jupyter Notebook and JupyterLab support rendering arbitrary MIME types many other notebook environments (such as VSCode notebooks) only support bi-directional communication channels when rendering an IPyWidget. Therefore Panel provides a compatibility wrapper that makes it possible to wrap a Panel component in an IPywidget. To enable ipywidgets support globally you can set the `comms` option:

```python
pn.extension(comms='ipywidgets')
# or
pn.config.comms = 'ipywidgets'
```

Note that this happens automatically when running Panel inside VSCode and Google Colab but may be needed in other notebook environments. This global setting can also be useful when trying to serve an entire notebook using [Voilà](https://github.com/voila-dashboards/voila). Alternatively, we can convert individual objects to an ipywidget one at a time using the `pn.ipywidget()` function:

```python
ipywidget = pn.ipywidget(pane)
ipywidget
```

This approach also allows combining a Panel object with any other Jupyter-widget--based model:

```python
from ipywidgets import Accordion
Accordion(children=[pn.ipywidget(pane)])
```

To use Panel's ipywidgets support in JupyterLab 4.x, install the Python packages (they ship prebuilt labextensions; you do **not** need `jupyter labextension install`):

```bash
pip install jupyter_bokeh ipywidgets
```

or using conda:

```bash
conda install -c conda-forge jupyter_bokeh ipywidgets
```

## Related Resources

- [JupyterLab support matrix](jupyterlab_support)
- [Preview apps in JupyterLab](jupyterlabpreview)

