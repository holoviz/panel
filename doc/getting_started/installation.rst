Installation
============

|CondaPyViz|_ |CondaDefaults|_ |PyPI|_ |License|_

Prerequisites
-------------

Before you can get started with Panel you are going to need a couple of things:

1. An IDE, text editor or notebook environment

2. Python 3.7 - Python 3.10

3. `pip <https://pip.pypa.io/en/stable/installation/>`_ or `conda <http://conda.pydata.org/docs/>`_

Setting up Python
------------------

The recommended way to install Panel on all operating systems is using the `conda <http://conda.pydata.org/docs/>`_ command provided by `Anaconda <http://docs.continuum.io/anaconda/install>`_ or `Miniconda <http://conda.pydata.org/miniconda.html>`_. If you are not familiar with command line interfaces we recommend you use the `Anaconda <http://docs.continuum.io/anaconda/install>`_ installer and use `Anaconda Navigator <https://docs.anaconda.com/anaconda/navigator>`_.

Alternatively you can also set up your own Python installation and manage your environment using a different environment management tool such as:

  - `pipenv <https://pipenv-fork.readthedocs.io/en/latest/>`_
  - `poetry <https://python-poetry.org/>`_
  - `virtualenv <https://virtualenv.pypa.io/en/latest/>`_

Installing Panel
----------------

Once you have set up Python and chosen an environment management tool install Panel using either ``conda``::

  conda install -c pyviz panel

or using ``pip``::

  pip install panel

Developing in different editors
-------------------------------

Editor + Server
^^^^^^^^^^^^^^^

You can edit your Panel code as a ``.py`` file in any text editor, marking the objects you want to render as ``.servable()``, then launch a server with::

  panel serve my_script.py --show --autoreload

to open a browser tab showing your app or dashboard and backed by a live Python process. The ``--autoreload`` flag ensures that the app reloads whenever you make a change to the Python source.

JupyterLab and Classic notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In the classic Jupyter notebook environment and JupyterLab, first make sure to load the ``pn.extension()``. Panel objects will then render themselves if they are the last item in a notebook cell. For versions of ``jupyterlab>=3.0`` the necessary extension is automatically bundled in the ``pyviz_comms`` package, which must be >=2.0.

However note that for version of ``jupyterlab<3.0`` you must also manually install the JupyterLab extension with::

  jupyter labextension install @pyviz/jupyterlab_pyviz

Google Colab
^^^^^^^^^^^^

In the Google Colaboratory notebook, first make sure to load the `pn.extension()`. Panel objects will then render themselves if they are the last item in a notebook cell. Please note that in Colab rendering for each notebook cell is isolated, which means that every cell must reload the Panel extension code separately. This will result in somewhat slower and larger notebook than with other notebook technologies.

VSCode notebook
^^^^^^^^^^^^^^^

Visual Studio Code (VSCode) versions 2020.4.74986 and later support ipywidgets, and Panel objects can be used as ipywidgets since Panel 0.10 thanks to `jupyter_bokeh`, which means that you can now use Panel components interactively in VSCode. Ensure you install `jupyter_bokeh` with `pip install jupyter_bokeh` or `conda install -c bokeh jupyter_bokeh` and then enable the extension with `pn.extension()`.

nteract and other ipywidgets notebooks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In other notebook environments that support rendering ipywidgets interactively, such as nteract, you can use the same underlying ipywidgets support as for vscode: Install ``jupyter_bokeh`` and then use ``pn.extension(comms='ipywidgets')``.

Other environments
^^^^^^^^^^^^^^^^^^

If your development environment offers embedded Python processes but does not support ipywidgets or Jupyter "comms" (communication channels), you will notice that some or all interactive functionality is missing. Some widgets that operate only in JavaScript will work fine, but others require communication channels between JavaScript and Python. In such cases you can either request ipywidgets or Panel support from the editor or environment, or else use the Editor + Server approach above.

Get help
--------

If you get stuck for any reason come join our `helpful community Discourse forum <https://discourse.holoviz.org/c/panel/5>`_ and someone will come to your aid.

.. |CondaPyViz| image:: https://img.shields.io/conda/v/pyviz/panel.svg
.. _CondaPyViz: https://anaconda.org/pyviz/panel

.. |CondaDefaults| image:: https://img.shields.io/conda/v/anaconda/panel.svg?label=conda%7Cdefaults
.. _CondaDefaults: https://anaconda.org/anaconda/panel

.. |PyPI| image:: https://img.shields.io/pypi/v/panel.svg
.. _PyPI: https://pypi.python.org/pypi/panel

.. |License| image:: https://img.shields.io/pypi/l/panel.svg
.. _License: https://github.com/pyviz/panel/blob/master/LICENSE.txt
