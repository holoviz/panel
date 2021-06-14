.. _devguide_testing:

Testing
=======

This chapter describes how to run various tests locally in a
development environment, guidelines for writing tests, and information
regarding the continuous testing infrastructure.

.. contents::
    :local:
    :depth: 2

Running Tests Locally
---------------------

Before attempting to run Panel tests, make sure you have successfully
run through all of the instructions in the :ref:`devguide_setup`
section of the Developer's Guide.

Test Selection
~~~~~~~~~~~~~~

Currently Panel uses linting and two types of tests regular unit tests
which are run with pytest and notebook example tests run with nbsmoke:

To run flake checking use:

.. code-block:: sh

    doit test_flakes

To run unit tests use:

.. code-block:: sh

    doit test_unit

To run example smoke tests use:

.. code-block:: sh

    doit test_examples

Integration tests
~~~~~~~~~~~~~~~~~

Writing Tests
-------------

In order to help keep Panel maintainable, all Pull Requests that touch
code should normally be accompanied by relevant tests. While
exceptions may be made for specific circumstances, the default
assumption should be that a Pull Request without tests may not be
merged.

Python Unit Tests
~~~~~~~~~~~~~~~~~

Python unit tests maintain the basic functionality of the Python
portion of the Panel library. A few general guidelines will help you
write Python unit tests:

absolute imports
    In order to ensure that Panel's unit tests as relocatable and unambiguous
    as possible, always prefer absolute imports in test files. When convenient,
    import and use the entire module under test:

    * **GOOD**: ``import panel.widgets``
    * **GOOD**: ``from panel.layout import Column``
    * **BAD**: ``from ..models.widgets import Player``

pytest
    All new tests should use and assume `pytest`_ for test running, fixtures,
    parameterized testing, etc. New tests should *not* use the ``unittest``
    module of the Python standard library.

Continuous Integration
----------------------

Every push to the `master` branch or any Pull Request branch on GitHub
automatically triggers a full test build on the `GitHub Actions`_ continuous
integration service. This is most often useful for running the full Panel
test suite continuously, but also triggers automated scripts for publishing
releases when a tagged branch is pushed.

You can see the list of all current and previous builds at this URL:
https://github.com/holoviz/panel/actions

Configuration
~~~~~~~~~~~~~

There are a number of files that affect the build configuration:

* `.github/worksflows/test.yaml`
    Defines the build matrix and global configurations for the stages
    described below.

* `conda.recipe/meta.yaml`
    Instructions for building a conda noarch package for Panel.

* `setup.py`
    Used to build sdist packages and "dev" installs. This file is the
    single source of truth of all dependencies.

* `tox.ini`
    Contains the configuration for the doit commands .

Etiquette
~~~~~~~~~

GitHub Actions provides free build workers to Open Source projects. A few
considerations will help you be considerate of others needing these limited
resources:

* Group commits into meaningful chunks of work before pushing to GitHub (i.e.
  don't push on every commit).

* If you must make multiple commits in succession, navigate to GitHub Actions and
  cancel all but the last build, in order to free up build workers.

.. _contact the developers: https://gitter.im/pyviz/pyviz
.. _pytest: https://docs.pytest.org
.. _GitHub Actions: https://github.com/features/actions
