.. raw:: html

  <h1><img src="_static/logo_stacked.png" width="125"></h1>


A high-level app and dashboarding solution for Python
-----------------------------------------------------

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

Panel lets you move the same code freely between an interactive `Jupyter Notebook <http://jupyter.org>`__ prompt and a fully deployable standalone server.  That way you can easily switch between exploring your data, building visualizations, adding custom interactivity, sharing with non-technical users, and back again at any point, using the same tools and the same code throughout. Panel thus helps support your entire workflow, so that you never have to commit to only one way of using your data and your analyses, and don't have to rewrite your code just to make it usable in a different way.

Some example Panel apps: (Click on the title to see the code, or the image to deploy on mybinder if it has resources available.)


.. raw:: html

   <style>table {border-spacing: 15px} td { border: 1px solid black; vertical-align: top} </style>
   <table>
     <tr>
       <td border=1><a href="https://anaconda.org/jbednar/datashadercliffordinteract"><b>Interact</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/clifford-interact/master?urlpath=/proxy/5006/app"><img src="_static/collage/interact.png" /></a></td>
       <td border=1><a href="https://anaconda.org/jbednar/panel_gapminders"><b>Gapminders</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/gapminder/master?urlpath=/proxy/5006/app"><img src="_static/collage/gapminders.png" /></a></td>
       <td border=1><a href="https://anaconda.org/jbednar/nyc_taxi_panel"><b>NYC Taxi</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/nyc_taxi/master?urlpath=/proxy/5006/app"><img src="_static/collage/nyc_taxi.png" /></a></td>
       <td border=1><a href="https://anaconda.org/jbednar/glaciers"><b>Glaciers</b></a><br><a href="https://mybinder.org/v2/gh/panel-demos/glaciers/master?urlpath=/proxy/5006/app"><img src="_static/collage/glaciers.png" /></a></td>
       <td border=1><a href="https://anaconda.org/jbednar/eulersmethod"><b>Euler's Method</b></a><br><a href="https://anaconda.org/jbednar/eulersmethod"><img src="_static/collage/eulers_method.png" /></a></td>
     <tr>
   </table>


Using Panel for declarative, reactive programming
-------------------------------------------------

Panel can also be used with the separate `Param <http://param.pyviz.org>`__ project to create interactively configurable objects with or without associated visualizations, in a fully declarative way. With this approach, you declare your configurable object using the pure-Python, zero-dependency ``param`` library, annotating your code with parameter ranges, documentation, and dependencies between parameters and your code. Using this information, you can make all of your domain-specific code be optionally configurable in a GUI, with optional visual displays and debugging information if you like, all with just a few lines of declarations. With this approach, you don't ever have to commit to whether your code will be used in a notebook, in a GUI app, or completely behind the scenes in batch processing or reports -- the same code can support all of these cases equally well, once you declare the associated parameters and constraints. This approach lets you completely separate your domain-specific code from anything to do with web browsers, GUI toolkits, or other volatile technologies that would otherwise make your hard work become obsolete as they change over time. 

The `User Guide <user_guide>`_ explains how to use Panel.  Panel is currently in prerelease status, which means that it is available for public use but has an API that is expected to change with each new release without detailed notice. 

If you have any `issues <https://github.com/pyviz/panel/issues>`_ or wish to `contribute code <https://help.github.com/articles/about-pull-requests>`_, you can visit our `GitHub site <https://github.com/pyviz/panel>`_ or chat with the developers on `gitter <https://gitter.im/ioam/holoviews>`_.


Installation
------------

|CondaPkg|_ |PyPI|_ |License|_


Panel works with `Python 2.7 and Python 3 <https://travis-ci.org/pyviz/panel>`_ on Linux, Windows, or Mac.  The recommended way to install Panel is using the `conda <http://conda.pydata.org/docs/>`_ command provided by `Anaconda <http://docs.continuum.io/anaconda/install>`_ or `Miniconda <http://conda.pydata.org/miniconda.html>`_::

  conda install -c pyviz panel

or using PyPI::

  pip install panel

Support for classic Jupyter Notebook is included with Panel. If you want to work with JupyterLab, you will also need to install the optional PyViz JupyterLab extension::

  conda install -c conda-forge jupyterlab
  jupyter labextension install @pyviz/jupyterlab_pyviz

  
Getting Started
---------------

Once you've installed Panel, you can get your own copy of all the examples shown on this website::

  panel examples
  cd panel-examples

And then you can launch Jupyter to explore them yourself using either Jupyter Notebook or JupyterLab::

  jupyter notebook
  jupyter lab


PyViz
-----

Panel is part of the PyViz family of tools.  The `PyViz website <http://pyviz.org>`_
shows how to use Panel together with other libraries to solve complex problems,
with detailed tutorials and examples.


.. |PyPI| image:: https://img.shields.io/pypi/v/panel.svg
.. _PyPI: https://pypi.python.org/pypi/panel

.. |CondaPkg| image:: https://anaconda.org/pyviz/panel/badges/installer/conda.svg
.. _CondaPkg: https://anaconda.org/pyviz/panel

.. |License| image:: https://img.shields.io/pypi/l/panel.svg
.. _License: https://github.com/pyviz/panel/blob/master/LICENSE.txt


.. toctree::
   :titlesonly:
   :hidden:
   :maxdepth: 2

   Home <self>
   User Guide <user_guide/index>
   Topics <topics/index>
   Roadmap <Roadmap>
   FAQ
   Github source <http://github.com/pyviz/panel>
   About <about>
   
