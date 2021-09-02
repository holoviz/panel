<img src="https://github.com/holoviz/panel/raw/master/doc/_static/logo_horizontal_light_theme.png" data-canonical-src="https://github.com/holoviz/panel/raw/master/doc/_static/logo_stacked.png" width="400"/><br>

-----------------

# A high-level app and dashboarding solution for Python

|    |    |
| --- | --- |
| Build Status | [![Linux/MacOS Build Status](https://github.com/holoviz/panel/workflows/pytest/badge.svg?query=branch%3Amaster)](https://github.com/holoviz/panel/actions/workflows/test.yaml?query=branch%3Amaster)
| Coverage | [![codecov](https://codecov.io/gh/holoviz/panel/branch/master/graph/badge.svg)](https://codecov.io/gh/holoviz/panel) |
| Latest dev release | [![Github tag](https://img.shields.io/github/v/tag/holoviz/panel.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/panel/tags) [![dev-site](https://img.shields.io/website-up-down-green-red/https/pyviz-dev.github.io/panel.svg?label=dev%20website)](https://pyviz-dev.github.io/panel/) |
| Latest release | [![Github release](https://img.shields.io/github/release/holoviz/panel.svg?label=tag&colorB=11ccbb)](https://github.com/holoviz/panel/releases) [![PyPI version](https://img.shields.io/pypi/v/panel.svg?colorB=cc77dd)](https://pypi.python.org/pypi/panel) [![panel version](https://img.shields.io/conda/v/pyviz/panel.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/panel) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/panel.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/panel) [![defaults version](https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/panel) |
| Docs | [![gh-pages](https://img.shields.io/github/last-commit/holoviz/panel/gh-pages.svg)](https://github.com/holoviz/panel/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/https/panel.holoviz.org.svg)](https://panel.holoviz.org) |
| Binder | [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/holoviz/panel/v0.12.1?urlpath=lab/tree/examples) |
| Support | [![Discourse](https://img.shields.io/discourse/status?server=https%3A%2F%2Fdiscourse.holoviz.org)](https://discourse.holoviz.org/) |

## What is it?

Panel provides tools for easily composing widgets, plots, tables, and other viewable objects and controls into custom analysis tools, apps, and dashboards. Panel works with visualizations from [Bokeh](https://bokeh.pydata.org), [Matplotlib](https://matplotlib.org/), [HoloViews](https://holoviews.org), and many other Python plotting libraries, making them instantly viewable either individually or when combined with interactive widgets that control them.  Panel works equally well in [Jupyter Notebooks](http://jupyter.org), for creating quick data-exploration tools, or as standalone deployed apps and dashboards, and allows you to easily switch between those contexts as needed.

Panel makes it simple to make:

- Plots with user-defined controls
- Property sheets for editing parameters of objects in a workflow
- Control panels for simulations or experiments
- Custom data-exploration tools
- Dashboards reporting key performance indicators (KPIs) and trends
- Data-rich Python-backed web servers
- and anything in between

Panel objects are reactive, immediately updating to reflect changes to their state, which makes it simple to compose viewable objects and link them into simple, one-off apps to do a specific exploratory task.  The same objects can then be reused in more complex combinations to build more ambitious apps, while always sharing the same code that works well on its own.

   <table>
     <tr>
       <td border=1><a href="https://examples.pyviz.org/attractors/attractors_panel.html"><b>Attractors</b></a><br><a href="https://attractors.pyviz.demo.anaconda.com/attractors_panel"><img src="http://assets.holoviews.org/panel/thumbnails/index/attractors.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/gapminders/gapminders.html"><b>Gapminders</b></a><br><a href="https://gapminders.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/gapminders.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/nyc_taxi/dashboard.html"><b>NYC Taxi</b></a><br><a href="https://nyc-taxi.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/nyc_taxi.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/glaciers/glaciers.html"><b>Glaciers</b></a><br><a href="https://glaciers.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/glaciers.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/portfolio_optimizer/portfolio.html"><b>Portfolio Optimizer</b></a><br><a href="https://portfolio-optimizer.pyviz.demo.anaconda.com"><img src="http://assets.holoviews.org/panel/thumbnails/index/portfolio_optimizer.png" /></a></td>
     <tr>
   </table>

## Using Panel for declarative, reactive programming

Panel can also be used with the separate [Param](https://param.pyviz.org) project to create interactively configurable objects with or without associated visualizations, in a fully declarative way. With this approach, you declare your configurable object using the pure-Python, zero-dependency `param` library, annotating your code with parameter ranges, documentation, and dependencies between parameters and your code.  Using this information, you can make all of your domain-specific code be optionally configurable in a GUI, with optional visual displays and debugging information if you like, all with just a few lines of declarations. With this approach, you don't ever have to commit to whether your code will be used in a notebook, in a GUI app, or completely behind the scenes in batch processing or reports -- the same code can support all of these cases equally well, once you declare the associated parameters and constraints. This approach lets you completely separate your domain-specific code from anything to do with web browsers, GUI toolkits, or other volatile technologies that would otherwise make your hard work become obsolete as they change over time.

## Usage

Panel can be used in a wide range of development environments:

### Editor + Server

You can edit your Panel code as a .py file in any text editor, marking the objects you want to render as `.servable()`, then launch a server with `panel serve my_script.py --show` to open a browser tab showing your app or dashboard and backed by a live Python process. If you want the server to automatically reload when you save code changes during development, then you should use `panel serve my_script.py --auto --show`.

### JupyterLab and Classic notebook

In the classic Jupyter notebook environment and JupyterLab, first make sure to load the `pn.extension()`. Panel objects will then render themselves if they are the last item in a notebook cell. For versions of `jupyterlab>=3.0` the necessary extension is automatically bundled in the `pyviz_comms` package, which must be >=2.0. However note that for version of `jupyterlab<3.0` you must also manually install the JupyterLab extension with:

```bash
jupyter labextension install @pyviz/jupyterlab_pyviz
```

### Google Colab

In Google Colaboratory, rendering for each notebook cell is isolated, which means that every cell must reload the Panel extension code separately. Panel can do this automatically when you first load the extension if you declare that you are running in Colab: `pn.extension(comms='colab')`. Otherwise you will need to put `pn.extension()` in each cell where you want to display Panel output. Either way, you should be able to have access to all of Panel's functionality, though with a larger notebook size than with other notebook technologies that allow display code to be shared across cells.

### VSCode

Visual Studio Code (VSCode) versions 2020.4.74986 and later support ipywidgets, and Panel objects can be used as ipywidgets since Panel 0.10 thanks to `jupyter_bokeh`, which means that you can now use Panel components interactively in VSCode. Ensure you install `jupyter_bokeh` with `pip install jupyter_bokeh` or `conda install -c bokeh jupyter_bokeh` and then enable the extension with `pn.extension(comms='vscode')`.

### nteract and other ipywidgets notebooks

In other notebook environments that support rendering ipywidgets interactively, such as nteract, you can use the same underlying ipywidgets support as for vscode: Install `jupyter_bokeh` and then use `pn.extension(comms='ipywidgets')`.

### Other environments

If your development environment offers embedded Python processes but does not support ipywidgets or Jupyter "comms" (communication channels), you will notice that some or all interactive functionality is missing. Some widgets that operate only in JavaScript will work fine, but others require communication channels between JavaScript and Python. In such cases you can either request ipywidgets or Panel support from the editor or environment, or else use the Editor + Server approach above.


## Sponsors

The Panel project is grateful for the sponsorship by the organizations and companies below:

<table align="center">
<tr>
  <td>
    <a href="https://www.anaconda.com/">
      <img src="https://static.bokeh.org/sponsor/anaconda.png"
         alt="Anaconda Logo" width="200"/>
	 </a>
  </td>
  <td colspan="2">
    <a href="https://www.blackstone.com/the-firm/">
    <img src="https://static.bokeh.org/sponsor/blackstone.png"
         alt="Blackstone Logo" width="400"/>
    </a>
  </td>
</tr>
</table>
