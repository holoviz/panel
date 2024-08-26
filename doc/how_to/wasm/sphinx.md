# Embedding in Sphinx documentation

One more option is to include live Panel examples in your Sphinx documentation using the `nbsite.pyodide` directive.

## Setup

In the near future we hope to make this a separate Sphinx extension, until then simply install latest nbsite with `pip` or `conda`:

::::{tab-set}

:::{tab-item} Pip
:sync: pip

``` bash
pip install nbsite
```
:::

:::{tab-item} Conda
:sync: conda

``` bash
conda install -c pyviz nbsite
```
:::

::::

add the extension to the Sphinx `conf.py`:

```python
extensions += [
    ...,
    'nbsite.pyodide'
]
```

## Configuration

In the `conf.py` of your project you can configure the extension in a number of ways by defining an `nbsite_pyodide_conf` dictionary with the following options:

- `PYODIDE_URL`: The URl to fetch Pyodide from
- `autodetect_deps` (default=`True`): Whether to automatically detect dependencies in the executed code and install them.
- `enable_pwa` (default=`True`): Whether to add a web manifest and service worker to configure the documentation as a progressive web app.
- `requirements` (default=`['panel']`): Default requirements to include (by default this includes just panel.
- `scripts`: Scripts to add to the website when a Pyodide cell is first executed.
- `setup_code` (default=`''`): Python code to run when initializing the Pyodide runtime.

and then you can use the `pyodide` as an RST directive:

```rst
.. pyodide::

   import panel as pn

   slider = pn.widgets.FloatSlider(start=0, end=10, name='Amplitude')

   def callback(new):
       return f'Amplitude is: {new}'

   pn.Row(slider, pn.bind(callback, slider))
```

## Examples

The resulting output looks like this:

```{pyodide}
import panel as pn
```


```{pyodide}
slider = pn.widgets.FloatSlider(start=0, end=10, name='Amplitude')

def callback(new):
    return f'Amplitude is: {new}'

pn.Row(slider, pn.bind(callback, slider))
```

In addition to rendering Panel components it also renders regular Python
types:

```{pyodide}
1+1
```


```{pyodide}
"A string"
```

and also handles stdout and stderr streams:

```{pyodide}
import numpy as np
for i in range(10):
    print(f'Repeat {i}')
    for i in range(10000):
        np.random.rand(1000)
```

```{pyodide}
raise ValueError('Encountered an error')
```

and supports `_repr_<mime>_` methods that are commonly used by the IPython and Jupyter ecosystem:

```{pyodide}
class HTML:

    def __init__(self, html):
	    self.html = html

    def _repr_html_(self):
	    return self.html

HTML('<b>HTML!</b>')
```

## Usage

The code cell will display a button to execute the cell, which will warn about downloading the Python runtime on first-click and ask you to confirm whether you want to proceed. It will then download Pyodide, all required packages and finally display the output.
