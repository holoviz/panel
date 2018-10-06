.. raw:: html

  <h1><img src="_static/logo_stacked.png" width="125"></h1>


**A high-level dashboarding solution for Python visualization libraries**

Panel is an `open-source <https://github.com/pyviz/panel/blob/master/LICENSE.txt>`_ Python library.  Panel is currently in prerelease status, which means that it is available for public use but has an API that is expected to change with each new release without detailed notice.

The `User Guide <user_guide>`_ explains how to use Panel.

If you have any `issues <https://github.com/pyviz/panel/issues>`_ or wish to `contribute code <https://help.github.com/articles/about-pull-requests>`_, you can visit our `GitHub site <https://github.com/pyviz/panel>`_ or chat with the developers on `gitter <https://gitter.im/ioam/holoviews>`_.


Installation
____________

|CondaPkg|_ |PyPI|_ |License|_


Panel works with `Python 2.7 and Python 3 <https://travis-ci.org/pyviz/panel>`_ on Linux, Windows, or Mac, and provides optional extensions for working with `Jupyter Notebook and Jupyter Lab <http://jupyter.org>`_.

The recommended way to install Panel is using the `conda <http://conda.pydata.org/docs/>`_ command provided by `Anaconda <http://docs.continuum.io/anaconda/install>`_ or `Miniconda <http://conda.pydata.org/miniconda.html>`_::

  conda install -c pyviz/label/dev panel


PyViz
-----

Panel is part of the PyViz family of tools.  The `PyViz website <http://pyviz.org>`_
shows how to use Panel together with other libraries to solve complex problems,
including detailed tutorials and examples.


Usage
-----

Once you've installed Panel, you can get a copy of all the examples shown on this website::

  panel --install-examples
  cd panel-examples

And then you can launch Jupyter Notebook to explore them::

  jupyter notebook

To work with JupyterLab you will also need the PyViz JupyterLab
extension::

  conda install -c conda-forge jupyterlab
  jupyter labextension install @pyviz/jupyterlab_pyviz

Once you have installed JupyterLab and the extension launch it with::

  jupyter-lab



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
   
