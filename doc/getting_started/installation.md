# {octicon}`desktop-download;2em;sd-mr-1` Installation

[![conda pyviz badge](https://img.shields.io/conda/v/pyviz/panel.svg)](https://anaconda.org/pyviz/panel)
[![conda defaults badge](https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults)](https://anaconda.org/anaconda/panel)
[![PyPI badge](https://img.shields.io/pypi/v/panel.svg)](https://pypi.python.org/pypi/panel)
[![License badge](https://img.shields.io/pypi/l/panel.svg)](https://github.com/holoviz/panel/blob/main/LICENSE.txt)

Panel is compatible with Python 3.9 or later and works seamlessly on Linux, Windows, and Mac.

## Setup

:::::{tab-set}

::::{tab-item} pip
:sync: pip

:::{note}
Before proceeding, ensure you have Python installed on your system. If not, you can download and install Python from [Python.org](https://www.python.org/downloads/).

When using `pip`, it's important to keep your default Python environment clean. Utilize [virtual environments](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) to isolate your projects effectively.
:::

::::

::::{tab-item} conda
:sync: conda

:::{note}
Before proceeding, make sure you have either [Anaconda or Miniconda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) installed on your system. If not, you can find installation instructions [here](https://conda.io/projects/conda/en/latest/user-guide/install/index.html).

When using `conda`, it's crucial to maintain a clean base environment. Consider  [creating separate environments](https://conda.io/projects/conda/en/latest/user-guide/getting-started.html) to manage your projects efficiently.
:::

::::

:::::

## Installing Panel

Now, let's get Panel installed on your system.

:::::{tab-set}

::::{tab-item} pip
:sync: pip

```bash
pip install panel watchfiles
```

::::

::::{tab-item} conda
:sync: conda

```bash
conda install panel watchfiles
```

::::

:::::

:::{tip}
We recommend also installing [`watchfiles`](https://watchfiles.helpmanual.io) while developing. This will provide a significantly better experience when using Panel's `--autoreload` feature. It's not needed for production.
:::

:::{tip}

To incorporate highlighted code sections into your app, you'll need to install [`pygments`](https://pygments.org/), a powerful syntax highlighting library.
:::

:::{important}
Make sure Panel is installed in the same environment as JupyterLab/Jupyter Notebook (`pip install panel` or `conda install panel`) to ensure all features work correctly.
:::

:::{seealso}
If you plan to use Panel in a non-Jupyter notebook environment, such as Google Colab or VSCode, refer to the [relevant how-to section](../how_to/notebook/other_nb.md).
:::

## Next Steps

Now that you have installed Panel, let's [build a simple application](build_app.md).
