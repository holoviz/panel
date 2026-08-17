# Develop in other notebook environments

This guide addresses how to develop apps in Google Colab, VSCode, nteract, and other environments.

---

## Google Colab

In the Google Colaboratory notebook, first make sure to load the `pn.extension()`. As usual Panel objects will then render themselves if they are the last item in a notebook cell.

![Colab Panel Notebook](../../_static/images/colab-notebook.png)

## PyCharm Notebook

PyCharm Professional offers support for [notebooks](https://www.jetbrains.com/help/pycharm/ipython-notebook-support.html) and [ipywidgets](https://www.jetbrains.com/help/pycharm/interactive-js-widgets.html). Thanks to the `jupyter_bokeh` integration, Panel objects can be utilized as ipywidgets, allowing for interactive use of Panel components within PyCharm Professional. To ensure full functionality, install `jupyter_bokeh` using `pip install jupyter jupyter_bokeh` or `conda install jupyter jupyter_bokeh`, followed by activating the extension with `pn.extension()`.

For additional guidance, refer to the [How-To Configure PyCharm Guide](../editor/pycharm_configure).

## VSCode notebook

Visual Studio Code (VS Code) supports notebooks and ipywidgets, and Panel objects can be used as ipywidgets thanks to `jupyter_bokeh`, which means that you can use Panel components interactively in VS Code. Ensure you install `jupyter_bokeh` with `pip install jupyter_bokeh` or `conda install -c bokeh jupyter_bokeh` and then enable the extension with `pn.extension()`.

See also the [How-To Configure VS Code Guide](../editor/vscode_configure).

## nteract and other ipywidgets notebooks

In other notebook environments that support rendering ipywidgets interactively, such as nteract, you can use the same underlying ipywidgets support as for vscode: Install ``jupyter_bokeh`` and then use ``pn.extension(comms='ipywidgets')``.

## Marimo

Panel support has been added to Marimo at the end of 2024 through a collaboration between the Panel and Marimo teams, as describe in this PR: [marimo-team/marimo#2719](https://github.com/marimo-team/marimo/pull/2719)

At a high-level it includes serializing Panel components to JSON, setting up bi-directional communications and registering formatters for HoloViz libraries including Panel components, param.rx and HoloViews plots.

For further details on the integration, please consult the PR.

## Other environments

If your development environment offers embedded Python processes but does not support ipywidgets or Jupyter "comms" (communication channels), you will notice that some or all interactive functionality is missing. Some widgets that operate only in JavaScript will work fine, but others require communication channels between JavaScript and Python. In such cases you can either request ipywidgets or Panel support from the editor or environment, or else use the Editor + Server approach above.

## Related Resources
