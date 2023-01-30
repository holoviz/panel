# Installation

[![conda pyviz badge](https://img.shields.io/conda/v/pyviz/panel.svg)](https://anaconda.org/pyviz/panel)
[![conda defaults badge](https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults)](https://anaconda.org/anaconda/panel)
[![PyPI badge](https://img.shields.io/pypi/v/panel.svg)](https://pypi.python.org/pypi/panel)
[![License badge](https://img.shields.io/pypi/l/panel.svg)](https://github.com/holoviz/panel/blob/main/LICENSE.txt)

## Prerequisites

Before you can get started with Panel you are going to need a couple of things:

1. An IDE, text editor or notebook environment

2. Python 3.7 - Python 3.10

3. [pip](https://pip.pypa.io/en/stable/installation/) or [conda](https://conda.pydata.org/docs/)

## Setting up Python

The recommended way to install Panel on all operating systems is using the [conda](https://conda.pydata.org/docs/)_ command provided by [Anaconda](http://docs.continuum.io/anaconda/install) or [Miniconda](http://conda.pydata.org/miniconda.html). If you are not familiar with command line interfaces we recommend you use the [Anaconda](http://docs.continuum.io/anaconda/install) installer and use [Anaconda Navigator](https://docs.anaconda.com/anaconda/navigator).

Alternatively you can also set up your own Python installation and manage your environment using a different environment management tool such as:

- [pipenv](https://pipenv-fork.readthedocs.io/en/latest/)
- [poetry](https://python-poetry.org/)
- [virtualenv](https://virtualenv.pypa.io/en/latest/)

## Installing Panel

Once you have set up Python and chosen an environment management tool install Panel using either ``conda``:

```bash
conda install -c pyviz panel
```

or using ``pip``:

```bash
pip install panel
```

## Getting the examples

Most guides and examples that are rendered as part of the documentation are in fact written as Jupyter notebooks. We recommend that if you want to follow along with the examples you copy the examples to a local path, e.g. to copy to the current path use:

```bash
panel examples --path ./
```

Once the examples are copied switch to the directory you copied them to and launch a Jupyter notebook, e.g. with:

```bash
jupyter lab
```

Now you can navigate through the getting started and user guides and the various (reference) gallery examples.

## Developing in different editors

### Editor + Server

You can edit your Panel code as a ``.py`` file in any text editor, marking the objects you want to render as ``.servable()``, then launch a server with:

```bash
panel serve my_script.py --show --autoreload
```

to open a browser tab showing your app or dashboard and backed by a live Python process. The ``--autoreload`` flag ensures that the app reloads whenever you make a change to the Python source.

### JupyterLab and Classic notebook

In the classic Jupyter notebook environment and JupyterLab, first make sure to load the ``pn.extension()``. Panel objects will then render themselves if they are the last item in a notebook cell. For versions of ``jupyterlab>=3.0`` the necessary extension is automatically bundled in the ``pyviz_comms`` package, which must be >=2.0.

However note that for version of ``jupyterlab<3.0`` you must also manually install the JupyterLab extension with::
g
```
jupyter labextension install @pyviz/jupyterlab_pyviz
```

### Google Colab

In the Google Colaboratory notebook, first make sure to load the `pn.extension()`. Panel objects will then render themselves if they are the last item in a notebook cell. Please note that in Colab rendering for each notebook cell is isolated, which means that every cell must reload the Panel extension code separately. This will result in somewhat slower and larger notebook than with other notebook technologies.

### VSCode notebook

Visual Studio Code (VSCode) versions 2020.4.74986 and later support ipywidgets, and Panel objects can be used as ipywidgets since Panel 0.10 thanks to `jupyter_bokeh`, which means that you can now use Panel components interactively in VSCode. Ensure you install `jupyter_bokeh` with `pip install jupyter_bokeh` or `conda install -c bokeh jupyter_bokeh` and then enable the extension with `pn.extension()`.

### nteract and other ipywidgets notebooks

In other notebook environments that support rendering ipywidgets interactively, such as nteract, you can use the same underlying ipywidgets support as for vscode: Install ``jupyter_bokeh`` and then use ``pn.extension(comms='ipywidgets')``.

### Other environments

If your development environment offers embedded Python processes but does not support ipywidgets or Jupyter "comms" (communication channels), you will notice that some or all interactive functionality is missing. Some widgets that operate only in JavaScript will work fine, but others require communication channels between JavaScript and Python. In such cases you can either request ipywidgets or Panel support from the editor or environment, or else use the Editor + Server approach above.

## Get help

If you get stuck for any reason come join our [helpful community Discourse forum](https://discourse.holoviz.org/c/panel/5) and someone will come to your aid.
