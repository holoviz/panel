.. _devguide_setup:

Getting Set Up
==============

The Panel library is a complex project which provides a wide range
of data interfaces and an extensible set of plotting backends, which
means the development and testing process involves a wide set of
libraries.

.. contents::
    :local:
    :depth: 2

.. dev_guide_preliminaries:

Preliminaries
-------------

Git
~~~

The Panel source code is stored in a `Git`_ source control repository.
The first step to working on Panel is to install Git on to your system.
There are different ways to do this depending on whether, you are using
Windows, OSX, or Linux.

To install Git on any platform, refer to the `Installing Git`_ section of
the `Pro Git Book`_.

Conda
~~~~~

Developing Panel requires a wide range of packages that are not
easily and quickly available using pip. To make this more manageable,
core developers rely heavily on the `conda package manager`_ for the
free `Anaconda`_ Python distribution. However, ``conda`` can also
install non-Python package dependencies, which helps streamline Panel
development greatly. It is *strongly* recommended that anyone
developing Panel also use ``conda``, and the remainder of the
instructions will assume that ``conda`` is available.

To install Conda on any platform, see the `Download conda`_ section of the
`conda documentation`_.

Cloning the Repository
----------------------

The source code for the Panel project is hosted on GitHub_. To clone the
source repository, issue the following command:

.. code-block:: sh

    git clone https://github.com/pyviz/panel.git

This will create a ``panel`` directory at your file system
location. This ``panel`` directory is referred to as the *source
checkout* for the remainder of this document.

.. _dev_guide_installing_dependencies:

Installing Dependencies
-----------------------

Panel requires many additional packages for development and
testing. Many of these are on the main Anaconda default channel.

Conda Environments
~~~~~~~~~~~~~~~~~~

Since Panel interfaces with a large range of different libraries the
full test suite requires a wide range of dependencies. To make it
easier to install and run different parts of the test suite across
different platforms Panel uses a library called pyctdev to make things
more consistent and general.

.. code-block:: sh

    conda install -c pyviz "pyctdev>0.5.0"
    doit ecosystem_setup

Once pyctdev is available and you are in the cloned panel repository you can
set up an environment with:

.. code-block:: sh

    doit env_create -c pyviz/label/dev -c conda-forge --name=panel_dev --python=3.6

Specify the desired Python version, currently Panel officially
supports Python 2.7, 3.5, 3.6 and 3.7. Once the environment has been
created you can activate it with:

.. code-block:: sh

    conda activate panel_dev
    
Finally to install the dependencies required to run the full unit test
suite:

.. code-block:: sh

    doit develop_install -c pyviz/label/dev -c conda-forge -o tests -o recommended

.. _devguide_python_setup:

Building and Installing
-----------------------

Once you have all the required depencies installed, the simplest way
to build and install Panel to use the ``setup.py`` script at the top
level of the *source checkout* directory.

The ``setup.py`` script has two main modes of operation:

``python setup.py install``

    Panel will be installed in your Python ``site-packages`` directory.
    In this mode, any changes to the python source code will not show up
    until ``setup.py install`` is run again.

``python setup.py develop``

    Panel will be installed to refer to the source directory. Any changes
    you make to the python source code will be available immediately without
    any additional steps.


Next Steps
----------

If you have any problems with the steps here, please `contact the developers`_.

.. _Anaconda: https://anaconda.com/downloads
.. _contact the developers: https://gitter.im/pyviz/pyviz
.. _conda package manager: https://conda.io/docs/intro.html
.. _conda documentation: https://conda.io/docs/index.html
.. _Download conda: https://conda.io/docs/download.html
.. _Git: https://git-scm.com
.. _GitHub: https://github.com
.. _Installing Git: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
.. _Pro Git Book: https://git-scm.com/book/en/v2


.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    Getting Set up <index>
    Testing <testing>
