# Developer Guide

The Panel library is a complex project which provides a wide range of data interfaces and an extensible set of plotting backends, which means the development and testing process involves a wide set of libraries.

## Preliminaries

### Git

The Panel source code is stored in a [Git](https://git-scm.com) source control repository.  The first step to working on Panel is to install Git on to your system.  There are different ways to do this depending on whether, you are using Windows, OSX, or Linux.

To install Git on any platform, refer to the [Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) section of the [Pro Git Book](https://git-scm.com/book/en/v2).

### Conda

Developing Panel requires a wide range of packages that are not all easily available using pip. To make this more manageable, core developers rely heavily on the [conda package manager](https://conda.io/docs/intro.html) for the free [Anaconda](https://anaconda.com/downloads) Python distribution.

Particularly for non-Python package dependencies, ``conda`` helps streamline Panel development greatly. It is recommended (but not required) that you use ``conda`` (or ``mamba``).

To install Conda on any platform, see the [Download conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html) section of the `conda documentation`_.

## Cloning the Repository

The source code for the Panel project is hosted on [GitHub](https://github.com/holoviz/panel). To clone the source repository, issue the following command:

```bash
git clone https://github.com/holoviz/panel.git
```

This will create a ``panel`` directory at your file system location. This ``panel`` directory is referred to as the *source checkout* for the remainder of this document. Before continuing `cd` into the panel directory:

```bash
cd panel
```

## Create development environments

Panel uses [hatch](https://hatch.pypa.io/latest/version/) to build the library and set up development environments. It provides a number of environments to perform different tasks such as running tests, building the documentation etc.

Since many tasks require dependencies which are not easily installed with `pip` they use hybrid `conda` + `pip` environments. If you have not set up `conda` you will not be able to run these.

To set up `hatch` install it into your base environment:

```bash
pip install hatch hatch-conda
```

Once set up you can view the available environments with:

```bash
hatch env show
```

```
                            Standalone
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Name        ┃ Type    ┃ Features ┃ Dependencies ┃ Scripts       ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ default     │ virtual │          │              │               │
├─────────────┼─────────┼──────────┼──────────────┼───────────────┤
│ docs        │ conda   │ doc      │              │ build         │
│             │         │          │              │ build-pyodide │
│             │         │          │              │ generate-rst  │
│             │         │          │              │ refmanual     │
├─────────────┼─────────┼──────────┼──────────────┼───────────────┤
│ jupyterlite │ virtual │          │ jupyter      │ build         │
│             │         │          │ jupyterlite  │               │
└─────────────┴─────────┴──────────┴──────────────┴───────────────┘
                                       Matrices
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Name    ┃ Type    ┃ Envs           ┃ Features    ┃ Dependencies    ┃ Scripts        ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ test    │ conda   │ test.py3.8     │ examples    │ vtk             │ run            │
│         │         │ test.py3.9     │ recommended │ xgboost         │ run-coverage   │
│         │         │ test.py3.10    │ tests       │                 │ run-examples   │
│         │         │ test.py3.11    │             │                 │                │
│         │         │ test.py3.12    │             │                 │                │
├─────────┼─────────┼────────────────┼─────────────┼─────────────────┼────────────────┤
│ test-ui │ conda   │ test-ui.py3.8  │ recommended │ vtk             │ run            │
│         │         │ test-ui.py3.9  │ tests       │ xgboost         │ run-coverage   │
│         │         │ test-ui.py3.10 │ ui          │                 │ run-examples   │
│         │         │ test-ui.py3.11 │             │                 │ start-jupyter  │
│         │         │ test-ui.py3.12 │             │                 │                │
├─────────┼─────────┼────────────────┼─────────────┼─────────────────┼────────────────┤
│ pip     │ virtual │ pip.py3.8      │ all         │                 │ bundle         │
│         │         │ pip.py3.9      │             │                 │ example-test   │
│         │         │ pip.py3.10     │             │                 │ lint           │
│         │         │ pip.py3.11     │             │                 │ pyodide-wheels │
│         │         │ pip.py3.12     │             │                 │ ui-test        │
│         │         │                │             │                 │ unit-test      │
├─────────┼─────────┼────────────────┼─────────────┼─────────────────┼────────────────┤
│ dev     │ conda   │ dev.py3.8      │ all         │                 │ bundle         │
│         │         │ dev.py3.9      │             │                 │ example-test   │
│         │         │ dev.py3.10     │             │                 │ lint           │
│         │         │ dev.py3.11     │             │                 │ pyodide-wheels │
│         │         │ dev.py3.12     │             │                 │ ui-test        │
│         │         │                │             │                 │ unit-test      │
└─────────┴─────────┴────────────────┴─────────────┴─────────────────┴────────────────┘
```

For development we recommend using the `dev` environment. To create a `dev` environment and launch into the shell you can run:

```bash
hatch -e dev.py3.10 shell
```

Throughout the documentation we will use the Python 3.10 environment but you can select any supported Python version by replacing `py3.10` with the desired version. Once you are inside the environment you can confirm it is set up correctly with:

```bash
hatch run unit-test
```

## Pip-only environment

If you do not want to install `conda` we also offer a pure pip installation. We do not guarantee that this environment will be able to run the entire test suite and you also have to make sure you set up your own `nodejs>=16` (e.g. using [nvm](https://github.com/creationix/nvm) or [nvm-windows](https://github.com/coreybutler/nvm-windows)).

Once configured you can set up and launch the pip-only environment with:

```bash
hatch -e pip.py3.10 shell

## Clean up environments

The Panel environements can quickly grow in size, to clean up (i.e. remove) all the environments simply run:

```bash
hatch env prune
```

This will ensure that every time you make a commit linting will automatically be applied.

## Developing custom models

Panel ships with a number of custom Bokeh models, which have both Python and Javascript components. When developing Panel these custom models have to be compiled. This happens automatically with `pip install -e .`, however when running actively developing you can rebuild the extension with `panel build panel`. The `build` command is just an alias for `bokeh build`; see
the [Bokeh developer guide](https://docs.bokeh.org/en/latest/docs/dev_guide/setup.html) for more information about developing bokeh models.

Just like any other Javascript (or Typescript) library Panel defines a `package.json` and `package-lock.json` files. When adding, updating or removing a dependency in the package.json file ensure you commit the changes to the `package-lock.json` after running `npm install`.

## Bundling resources

Panel bundles external resources required for custom models and templates into the `panel/dist` directory. The bundled resources have to be collected whenever they change, so rerun `pip install -e .`  whenever you change one of the following:

* A new model is added with a `__javascript_raw__` declaration or an existing model is updated
* A new template with a `_resources` declaration is added or an existing template is updated
* A CSS file in one of template directories (`panel/template/*/`) is added or modified

## Next Steps

You will likely want to check out the [testing](testing.md) guide. Meanwhile, if you have any problems with the steps here, please visit our [Discourse](https://discourse.holoviz.org/c/panel/5).

## Useful Links

- [Dev version of Panel Site](https://holoviz-dev.github.io/panel)
   - Use this to explore new, not yet released features and docs
- [Panel main branch on Binder](https://mybinder.org/v2/gh/holoviz/panel/main?urlpath=lab/tree/examples)
   - Use this to quickly explore and manually test the newest panel features in a fresh environment with all requirements installed.
   - Replace `main` with `name-of-other-branch` for other branches.

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

testing
developing
docs
extensions
```
