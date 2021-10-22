***************
Getting Started
***************

Welcome to Panel!

This section will get you set up with Panel and provide a basic overview of the features and strengths of Panel. The `announcement blog <http://blog.pyviz.org/panel_announcement.html>`_ is another great resource to learn about the features of Panel and get an idea of what it can do.

Installation
------------

|CondaPyViz|_ |CondaDefaults|_ |PyPI|_ |License|_

Panel works with `Python 2.7 and Python 3 <https://travis-ci.org/pyviz/panel>`_ on Linux, Windows, or Mac.  The recommended way to install Panel is using the `conda <http://conda.pydata.org/docs/>`_ command provided by `Anaconda <http://docs.continuum.io/anaconda/install>`_ or `Miniconda <http://conda.pydata.org/miniconda.html>`_::

  conda install -c pyviz panel

or using PyPI::

  pip install panel

Support for classic Jupyter Notebook is included with Panel. If you want to work with JupyterLab, you will also need to install the optional PyViz JupyterLab extension::

  conda install -c conda-forge jupyterlab
  jupyter labextension install @pyviz/jupyterlab_pyviz


.. |CondaPyViz| image:: https://img.shields.io/conda/v/pyviz/panel.svg
.. _CondaPyViz: https://anaconda.org/pyviz/panel

.. |CondaDefaults| image:: https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults
.. _CondaDefaults: https://anaconda.org/anaconda/panel

.. |PyPI| image:: https://img.shields.io/pypi/v/panel.svg
.. _PyPI: https://pypi.python.org/pypi/panel

.. |License| image:: https://img.shields.io/pypi/l/panel.svg
.. _License: https://github.com/pyviz/panel/blob/master/LICENSE.txt

Development
-----------

Editor + Server
===============

You can edit your Panel code as a .py file in any text editor, marking the objects you want to render as ``.servable()``, then launch a server with ``panel serve my_script.py --show`` to open a browser tab showing your app or dashboard and backed by a live Python process.

JupyterLab and Classic notebook
===============================

In the classic Jupyter notebook environment and JupyterLab, first make sure to load the ``pn.extension()``. Panel objects will then render themselves if they are the last item in a notebook cell. For versions of ``jupyterlab>=3.0`` the necessary extension is automatically bundled in the ``pyviz_comms`` package, which must be >=2.0. However note that for version of ``jupyterlab<3.0`` you must also manually install the JupyterLab extension with::

  jupyter labextension install @pyviz/jupyterlab_pyviz

Google Colab
============

In Google Colaboratory, rendering for each notebook cell is isolated, which means that every cell must reload the Panel extension code separately. Panel can do this automatically when you first load the extension if you declare that you are running in Colab: ``pn.extension(comms='colab')``. Otherwise you will need to put ``pn.extension()`` in each cell where you want to display Panel output. Either way, you should be able to have access to all of Panel's functionality, though with a larger notebook size than with other notebook technologies that allow display code to be shared across cells.

VSCode
======

Visual Studio Code (VSCode) versions 2020.4.74986 and later support ipywidgets, and Panel objects can be used as ipywidgets since Panel 0.10 thanks to ``jupyter_bokeh``, which means that you can now use Panel components interactively in VSCode. Ensure you install ``jupyter_bokeh`` with ``pip install jupyter_bokeh`` or ``conda install -c bokeh jupyter_bokeh`` and then enable the extension with ``pn.extension(comms='vscode')``.

nteract and other ipywidgets notebooks
======================================

In other notebook environments that support rendering ipywidgets interactively, such as nteract, you can use the same underlying ipywidgets support as for vscode: Install ``jupyter_bokeh`` and then use ``pn.extension(comms='ipywidgets')``.

Other environments
==================
If your development environment offers embedded Python processes but does not support ipywidgets or Jupyter "comms" (communication channels), you will notice that some or all interactive functionality is missing. Some widgets that operate only in JavaScript will work fine, but others require communication channels between JavaScript and Python. In such cases you can either request ipywidgets or Panel support from the editor or environment, or else use the Editor + Server approach above.

Using Panel
-----------

.. notebook:: panel ../../examples/getting_started/Introduction.ipynb
