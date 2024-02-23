# {octicon}`desktop-download;2em;sd-mr-1` Installation

[![conda pyviz badge](https://img.shields.io/conda/v/pyviz/panel.svg)](https://anaconda.org/pyviz/panel)
[![conda defaults badge](https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults)](https://anaconda.org/anaconda/panel)
[![PyPI badge](https://img.shields.io/pypi/v/panel.svg)](https://pypi.python.org/pypi/panel)
[![License badge](https://img.shields.io/pypi/l/panel.svg)](https://github.com/holoviz/panel/blob/main/LICENSE.txt)
## Setup

Panel works with Python 3.8 or later on Linux, Windows, and Mac.

The recommended way to install Panel is using the [conda](https://docs.conda.io/projects/conda/en/latest/index.html) command that is included in the installation of [Anaconda or Miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html). Completing the installation for either Anaconda or Miniconda will also install Python.

:::{admonition} Note

To help you choose between Anaconda and Miniconda, review [this page](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#anaconda-or-miniconda).
:::

:::{admonition} Note
When you begin using conda, you already have a default environment named `base`. You don't want to install programs into your base environment, though. [Create separate environments](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) to keep your programs isolated from each other.
:::

If you choose not to install Anaconda or Miniconda, you can download Python directly from [Python.org](https://www.python.org/downloads/). In this case, you can install Panel using [pip](https://pip.pypa.io/en/stable/), which comes with Python.

## Installing Panel

Open up a terminal and run the following command, which will install Panel with all its dependencies.

::::{tab-set}

:::{tab-item} pip
:sync: pip

``` bash
pip install panel
```

:::

:::{tab-item} conda
:sync: conda

``` bash
conda install panel
```

:::

::::

:::{important}
Is Panel installed together with JupyterLab/Jupyter Notebook in your working environment? If not, you need to make sure that `pyviz_comms` is explicitly installed in the same environment as JupyterLab/Jupyter Notebook (`conda install pyviz_comms` or `pip install pyviz-comms`) for bi-directional communication to be fully working.
:::

:::{seealso}
If you intend to work with Panel in a non-Jupyter notebook environment such as VSCode have a quick at the [relevant how-to section](../how_to/notebook/other_nb.md).
:::

## Next Steps

Now that you have installed Panel, let's [build a simple application](build_app.md).
