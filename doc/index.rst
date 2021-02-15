.. raw:: html

  <h1><img src="_static/logo_stacked.png" width="125"></h1>


A high-level app and dashboarding solution for Python
-----------------------------------------------------

.. raw:: html

   <style>table {border-spacing: 15px} td { border: 1px solid black; vertical-align: top} </style>
   <table>
     <tr>
       <td border=1><a href="https://examples.pyviz.org/attractors/attractors_panel.html"><b>Attractors</b></a><br><a href="https://attractors.pyviz.demo.anaconda.com/attractors_panel"><img src="https://assets.holoviews.org/panel/thumbnails/index/attractors.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/gapminders/gapminders.html"><b>Gapminders</b></a><br><a href="https://gapminders.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/gapminders.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/nyc_taxi/dashboard.html"><b>NYC Taxi</b></a><br><a href="https://nyc-taxi.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/nyc_taxi.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/glaciers/glaciers.html"><b>Glaciers</b></a><br><a href="https://glaciers.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/glaciers.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/portfolio_optimizer/portfolio.html"><b>Portfolio Optimizer</b></a><br><a href="https://portfolio-optimizer.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/portfolio_optimizer.png" /></a></td>
     <tr>
   </table>

Panel is an `open-source <https://github.com/pyviz/panel/blob/master/LICENSE.txt>`_ Python library that lets you create custom interactive web apps and dashboards by connecting user-defined widgets to plots, images, tables, or text.

Compared to other approaches, Panel is novel in that it supports nearly all plotting libraries, works just as well in a Jupyter notebook as on a standalone secure web server, uses the same code for both those cases, supports both Python-backed and static HTML/JavaScript exported applications, and can be used to develop rich interactive applications without tying your domain-specific code to any particular GUI or web tools.

Panel makes it simple to make:

-  Plots with user-defined controls
-  Property sheets for editing parameters of objects in a workflow
-  Control panels for simulations or experiments
-  Custom data-exploration tools
-  Dashboards reporting key performance indicators (KPIs) and trends
-  Data-rich Python-backed web servers
-  and anything in between

Panel objects are reactive, immediately updating to reflect changes to their state, which makes it simple to compose viewable objects and link them into simple, one-off apps to do a specific exploratory task. The same objects can then be reused in more complex combinations to build more ambitious apps, while always sharing the same code that works well on its own.

Panel lets you move the same code freely between an interactive `Jupyter Notebook <https://jupyter.org>`__ prompt and a fully deployable standalone server.  That way you can easily switch between exploring your data, building visualizations, adding custom interactivity, sharing with non-technical users, and back again at any point, using the same tools and the same code throughout. Panel thus helps support your entire workflow, so that you never have to commit to only one way of using your data and your analyses, and don't have to rewrite your code just to make it usable in a different way. In many cases, using Panel can turn projects that used to take weeks or months into something you finish on the same day you started, creating a full Python-backed deployed web service for your visualized data in minutes or hours without having to run a software development project or hand your work over to another team.

Using Panel for declarative, reactive programming
-------------------------------------------------

Panel can also be used with the separate `Param <https://param.pyviz.org>`__ project to create interactively configurable objects with or without associated visualizations, in a fully declarative way. With this approach, you declare your configurable object using the pure-Python, zero-dependency ``param`` library, annotating your code with parameter ranges, documentation, and dependencies between parameters and your code. Using this information, you can make all of your domain-specific code be *optionally* configurable in a GUI, with *optional* visual displays and debugging information if you like, all with just a few lines of declarations. With this approach, you don't ever have to decide whether your code will eventually be used in a notebook, in a GUI app, or completely behind the scenes in batch processing, servers, or reports -- the same code can support all of these cases equally well, once you declare the associated parameters and constraints. This approach lets you completely separate your domain-specific code from anything to do with web browsers, GUI toolkits, or other volatile technologies that would otherwise make your hard work become obsolete as they change over time.

The `Getting Started <getting_started>`_ will provide a quick introduction to the panel API and get you started while the `User Guide <user_guide>`_ provides a more detailed guide on how to use Panel.

For usage questions or technical assistance, please head over to `Discourse <https://discourse.holoviz.org/>`_. If you have any `issues <https://github.com/pyviz/panel/issues>`_ or wish to `contribute code <https://help.github.com/articles/about-pull-requests>`_, you can visit our `GitHub site <https://github.com/pyviz/panel>`_.


Installation
------------

|CondaPyViz|_ |CondaDefaults|_ |PyPI|_ |License|_


Panel works with `Python 3 <https://github.com/holoviz/panel/actions?query=workflow%3Apytest>`_ on Linux, Windows, or Mac. The recommended way to install Panel is using the `conda <https://docs.conda.io/projects/conda/en/latest/index.html>`_ command provided by `Anaconda <https://docs.anaconda.com/anaconda/install/>`_ or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_::

  conda install -c pyviz panel

or using PyPI::

  pip install panel


Getting Started
---------------

Once you've installed Panel, you can get your own copy of all the notebooks used to make this website by running the following commands on the commandline in your conda or pip environment::

  panel examples
  cd panel-examples

And then you can launch Jupyter to explore them yourself using either Jupyter Notebook or JupyterLab (having first installed the extension!)::

  jupyter notebook
  jupyter lab

Usage
-----

Panel can be used in a wide range of development environments:

Editor + Server
===============

You can edit your Panel code as a .py file in any text editor, marking the objects you want to render as `.servable()`, then launch a server with `panel serve my_script.py --show` to open a browser tab showing your app or dashboard and backed by a live Python process.

JupyterLab and Classic notebook
===============================

In the classic Jupyter notebook environment and JupyterLab, first make sure to load the `pn.extension()`. Panel objects will then render themselves if they are the last item in a notebook cell. For versions of `jupyterlab>=3.0` the necessary extension is automatically bundled in the `pyviz_comms` package, which must be >=2.0. However note that for version of `jupyterlab<3.0` you must also manually install the JupyterLab extension with:

  jupyter labextension install @pyviz/jupyterlab_pyviz

Google Colab
============

In Google Colaboratory, rendering for each notebook cell is isolated, which means that every cell must reload the Panel extension code separately. Panel can do this automatically when you first load the extension if you declare that you are running in Colab: `pn.extension(comms='colab')`. Otherwise you will need to put `pn.extension()` in each cell where you want to display Panel output. Either way, you should be able to have access to all of Panel's functionality, though with a larger notebook size than with other notebook technologies that allow display code to be shared across cells.

VSCode
======

Visual Studio Code (VSCode) versions 2020.4.74986 and later support ipywidgets, and Panel objects can be used as ipywidgets since Panel 0.10 thanks to `jupyter_bokeh`, which means that you can now use Panel components interactively in VSCode. Ensure you install `jupyter_bokeh` with `pip install jupyter_bokeh` or `conda install -c bokeh jupyter_bokeh` and then enable the extension with `pn.extension(comms='vscode')`.

nteract and other ipywidgets notebooks
======================================

In other notebook environments that support rendering ipywidgets interactively, such as nteract, you can use the same underlying ipywidgets support as for vscode: Install `jupyter_bokeh` and then use `pn.extension(comms='ipywidgets')`.

Other environments
==================
If your development environment offers embedded Python processes but does not support ipywidgets or Jupyter "comms" (communication channels), you will notice that some or all interactive functionality is missing. Some widgets that operate only in JavaScript will work fine, but others require communication channels between JavaScript and Python. In such cases you can either request ipywidgets or Panel support from the editor or environment, or else use the Editor + Server approach above.


Sponsors
--------

The Panel project is grateful for the sponsorship by the organizations and companies below:

.. raw:: html

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

.. |CondaPyViz| image:: https://img.shields.io/conda/v/pyviz/panel.svg
.. _CondaPyViz: https://anaconda.org/pyviz/panel

.. |CondaDefaults| image:: https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults
.. _CondaDefaults: https://anaconda.org/anaconda/panel

.. |PyPI| image:: https://img.shields.io/pypi/v/panel.svg
.. _PyPI: https://pypi.python.org/pypi/panel

.. |License| image:: https://img.shields.io/pypi/l/panel.svg
.. _License: https://github.com/pyviz/panel/blob/master/LICENSE.txt


.. toctree::
   :titlesonly:
   :hidden:
   :maxdepth: 2

   Home <self>
   Getting Started <getting_started/index>
   User Guide <user_guide/index>
   Gallery <gallery/index>
   Reference Gallery <reference/index>
   Developer Guide <developer_guide/index>
   API <api/index>
   Comparisons <Comparisons>
   Releases <releases>
   Road Map <Roadmap>
   FAQ
   Github source <https://github.com/pyviz/panel>
   About <about>
