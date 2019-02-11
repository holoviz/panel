<img src="https://github.com/pyviz/panel/raw/master/doc/_static/logo_stacked.png" data-canonical-src="https://github.com/pyviz/panel/raw/master/doc/_static/logo_stacked.png" width="200"/><br>

-----------------

# A high-level app and dashboarding solution for Python

|    |    |
| --- | --- |
| Build Status | [![Linux/MacOS Build Status](https://travis-ci.org/pyviz/panel.svg?branch=master)](https://travis-ci.org/pyviz/panel) [![Windows Build status](https://img.shields.io/appveyor/ci/pyviz/panel/master.svg)](https://ci.appveyor.com/project/pyviz/panel/branch/master) |
| Coverage | [![codecov](https://codecov.io/gh/pyviz/panel/branch/master/graph/badge.svg)](https://codecov.io/gh/pyviz/panel) |
| Latest dev release | [![Github tag](https://img.shields.io/github/tag/pyviz/panel.svg?label=tag&colorB=11ccbb)](https://github.com/pyviz/panel/tags) |
| Latest release | [![Github release](https://img.shields.io/github/release/pyviz/panel.svg?label=tag&colorB=11ccbb)](https://github.com/pyviz/panel/releases) [![PyPI version](https://img.shields.io/pypi/v/panel.svg?colorB=cc77dd)](https://pypi.python.org/pypi/panel) [![panel version](https://img.shields.io/conda/v/pyviz/panel.svg?colorB=4488ff&style=flat)](https://anaconda.org/pyviz/panel) [![conda-forge version](https://img.shields.io/conda/v/conda-forge/panel.svg?label=conda%7Cconda-forge&colorB=4488ff)](https://anaconda.org/conda-forge/panel) [![defaults version](https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults&style=flat&colorB=4488ff)](https://anaconda.org/anaconda/panel) |
| Docs | [![gh-pages](https://img.shields.io/github/last-commit/pyviz/panel/gh-pages.svg)](https://github.com/pyviz/panel/tree/gh-pages) [![site](https://img.shields.io/website-up-down-green-red/http/panel.pyviz.org.svg)](http://panel.pyviz.org) |


## What is it?

Panel provides tools for easily composing widgets, plots, tables, and other viewable objects and controls into control panels, apps, and dashboards. Panel works with visualizations from [Bokeh](http://bokeh.pydata.org), [Matplotlib](matplotlib.org), [HoloViews](http://holoviews.org), and other Python plotting libraries, making them instantly viewable either individually or when combined with interactive widgets that control them.  Panel works equally well in [Jupyter Notebooks](http://jupyter.org), for creating quick data-exploration tools, or as standalone deployed apps and dashboards, and allows you to easily switch between those contexts as needed.

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
       <td border=1><a href="https://anaconda.org/jbednar/datashadercliffordinteract"><b>Interact</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/clifford-interact/master?urlpath=/proxy/5006/app"><img src="https://github.com/pyviz/panel/raw/master/doc/_static/collage/interact.png" /></a></td>
       <td border=1><a href="https://anaconda.org/jbednar/panel_gapminders"><b>Gapminders</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/gapminder/master?urlpath=/proxy/5006/app"><img src="https://github.com/pyviz/panel/raw/master/doc/_static/collage/gapminders.png" /></a></td>
       <td border=1><a href="https://anaconda.org/jbednar/nyc_taxi_panel"><b>NYC Taxi</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/nyc_taxi/master?urlpath=/proxy/5006/app"><img src="https://github.com/pyviz/panel/raw/master/doc/_static/collage/nyc_taxi.png" /></a></td>
       <td border=1><a href="https://anaconda.org/jbednar/glaciers"><b>Glaciers</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/glaciers/master?urlpath=/proxy/5006/app"><img src="https://github.com/pyviz/panel/raw/master/doc/_static/collage/glaciers.png" /></a></td>
     <tr>
   </table>

## Using Panel for declarative, reactive programming

Panel can also be used with the separate [Param](http://param.pyviz.org) project to create interactively configurable objects with or without associated visualizations, in a fully declarative way. With this approach, you declare your configurable object using the pure-Python, zero-dependency `param` library, annotating your code with parameter ranges, documentation, and dependencies between parameters and your code.  Using this information, you can make all of your domain-specific code be optionally configurable in a GUI, with optional visual displays and debugging information if you like, all with just a few lines of declarations. With this approach, you don't ever have to commit to whether your code will be used in a notebook, in a GUI app, or completely behind the scenes in batch processing or reports -- the same code can support all of these cases equally well, once you declare the associated parameters and constraints. This approach lets you completely separate your domain-specific code from anything to do with web browsers, GUI toolkits, or other volatile technologies that would otherwise make your hard work become obsolete as they change over time.

## About PyViz

Panel is part of the PyViz initiative for making Python-based visualization tools work well together.
See [pyviz.org](http://pyviz.org) for related packages that you can use with Panel and
[status.pyviz.org](http://status.pyviz.org) for the current status of each PyViz project.
