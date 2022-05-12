.. title:: Panel Documentation

.. raw:: html

  <img src="_static/logo_stacked.png" width="125">
  <h2 style="margin-top: 0.3em;">A high-level app and dashboarding solution for Python</h2>

   <table class="showcase-table">
     <tr>
       <td border=1><a href="https://examples.pyviz.org/attractors/attractors_panel.html"><b>Attractors</b></a><br><a href="https://attractors.pyviz.demo.anaconda.com/attractors_panel"><img src="https://assets.holoviews.org/panel/thumbnails/index/attractors.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/gapminders/gapminders.html"><b>Gapminders</b></a><br><a href="https://gapminders.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/gapminders.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/nyc_taxi/dashboard.html"><b>NYC Taxi</b></a><br><a href="https://nyc-taxi.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/nyc_taxi.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/glaciers/glaciers.html"><b>Glaciers</b></a><br><a href="https://glaciers.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/glaciers.png" /></a></td>
       <td border=1><a href="https://examples.pyviz.org/portfolio_optimizer/portfolio.html"><b>Portfolio Optimizer</b></a><br><a href="https://portfolio-optimizer.pyviz.demo.anaconda.com"><img src="https://assets.holoviews.org/panel/thumbnails/index/portfolio_optimizer.png" /></a></td>
     <tr>
   </table>
   <hr>

Panel is an `open-source <https://github.com/holoviz/panel/blob/master/LICENSE.txt>`_ Python library that lets you create custom interactive web apps and dashboards by connecting user-defined widgets to plots, images, tables, or text.

.. notebook:: panel ../examples/homepage.ipynb
    :disable_interactivity_warning: True

Compared to other approaches, Panel is novel in that it supports nearly all plotting libraries, works just as well in a Jupyter notebook as on a standalone secure web server, uses the same code for both those cases, supports both Python-backed and static HTML/JavaScript exported applications, and can be used to develop rich interactive applications without tying your domain-specific code to any particular GUI or web tools.

Panel makes it simple to:

- Use the PyData tools and plotting libraries that you know and love
- Develop in your favorite editor or notebook environment and seamlessly deploy the resulting application
- Iterate quickly to prototype apps and dashboards while offering polished templates for your final deployment
- Support deep interactivity by communicating client-side interactions and events to Python
- Stream data large and small to the frontend
- Add authentication to your application using the inbuilt OAuth providers

The `Getting Started <getting_started>`_ will provide a quick introduction to the panel API and get you started while the `User Guide <user_guide>`_ provides a more detailed guide on how to use Panel.

For usage questions or technical assistance, please head over to `Discourse <https://discourse.holoviz.org/>`_. If you have any `issues <https://github.com/holoviz/panel/issues>`_ or wish to `contribute code <https://help.github.com/articles/about-pull-requests>`_, you can visit our `GitHub site <https://github.com/holoviz/panel>`_.

Installation
------------

|CondaPyViz|_ |CondaDefaults|_ |PyPI|_ |License|_

Panel works with `Python 3 <https://github.com/holoviz/panel/actions?query=workflow%3Apytest>`_ on Linux, Windows, or Mac. The recommended way to install Panel is using the `conda <https://docs.conda.io/projects/conda/en/latest/index.html>`_ command provided by `Anaconda <https://docs.anaconda.com/anaconda/install/>`_ or `Miniconda <https://docs.conda.io/en/latest/miniconda.html>`_::

  conda install -c pyviz panel

or using PyPI::

  pip install panel

Usage
-----

Panel can be used in a wide range of development environments from a simple Python REPL, in a notebook or your favorite IDE such as VSCode. Visit the `Getting Started Guide <getting_started#installation>`_ to discover how to get set up in your favorite development environment.

Sponsors
--------

The Panel project is grateful for the sponsorship by the organizations and companies below:

.. raw:: html

    <table align="center">
    <tr>
      <td>
        <a href="https://www.anaconda.com/">
          <img src="https://static.bokeh.org/sponsor/anaconda.png"
             alt="Anaconda Logo" width="300"/>
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
   Developers <developer_guide/index>
   API <api/index>
   Releases <releases>
   FAQ
   About <about/index>
