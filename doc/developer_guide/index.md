# Developer Guide

The Panel library is a project which provides a wide range of data interfaces and an extensible set of plotting backends, which means the development and testing process involves a wide set of libraries.

This guide describes how to install and configure the development environment either simplified for first time contributors or fully as done by core developers.

If you have any problems with the steps here, please reach out in the `dev` channel on [Discord](https://discord.gg/rb6gPXbdAr) or on [Discourse](https://discourse.holoviz.org/).

## Preliminaries

### Basic understanding of how to contribute to Open Source

If this is your first open source contribution, please study one
or more of the below resources.

- [How to Get Started with Contributing to Open Source | Video](https://youtu.be/RGd5cOXpCQw)
- [Contributing to Open-Source Projects as a New Python Developer | Video](https://youtu.be/jTTf4oLkvaM)
- [How to Contribute to an Open Source Python Project | Blog post](https://www.educative.io/blog/contribue-open-source-python-project)

### Git

The Panel source code is stored in a [Git](https://git-scm.com) source control repository.  The first step to working on Panel is to install Git on to your system.  There are different ways to do this depending on whether, you are using Windows, OSX, or Linux.

To install Git on any platform, refer to the [Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) section of the [Pro Git Book](https://git-scm.com/book/en/v2).

In order to contribute to Panel you will also need [Github account](https://github.com/join) and knowledge of the [*fork and pull request workflow*](https://docs.github.com/en/get-started/quickstart/contributing-to-projects).

### Pip

First time contributors can get quickly up to speed using `pip` instead of `conda`.

### Conda

Developing all aspects of Panel requires a wide range of packages that are not easily and quickly available using pip. To make this more manageable, core developers rely heavily on the [conda package manager](https://conda.io/docs/intro.html) for the free [Anaconda](https://anaconda.com/downloads) Python distribution. However, ``conda`` can also install non-Python package dependencies, which helps streamline Panel development greatly. It is *strongly* recommended that any experienced or regular contributor use ``conda``.

To install Conda on any platform, see the [Download conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html) section of the `conda documentation`_.

## Cloning the Project

The source code for the Panel project is hosted on [GitHub](https://github.com/holoviz/panel).

### Non-core developer

To clone the source repository

- Go to [github.com/holoviz/panel](https://github.com/holoviz/panel)
- [Fork the repository](https://docs.github.com/en/get-started/quickstart/contributing-to-projects#forking-a-repository)
- Run

```bash
git clone https://github.com/<Your UserName Here>/panel.git
```

### Core developer

Core developers can work directly with the Panel repository. To clone run

```base
git clone https://github.com/holoviz/panel.git
```

## Installing the Project

The instructions for cloning above created a ``panel`` directory at your file system location. This ``panel`` directory is referred to as the *source checkout* for the remainder of this document. For the remainder of this document we will assume your current working directory is the *source checkout* directory.

### Fetch tags from upstream

Make sure to fetch tags from upstream repository before installing

```bash
git remote add upstream https://github.com/holoviz/panel.git
git fetch --tags upstream
git push --tags
```

### Basic Install with pip

We recommend this install to first time contributors that

- want to make a simple, quick contribution to notebooks, docs or the Python code
- can use pip to create and manage [virtual environments](https://realpython.com/python-virtual-environments-a-primer/).

Create a new virtual environment and activate it.

Run

```bash
pip install -e . jupyterlab pre-commit
panel bundle --all
pre-commit install
```

We install the [pre-commit](https://pre-commit.com/) package above to avoid pushing and reviewing code with obvious issues.

You can start Jupyter Lab by running

```bash
jupyter lab
```

If you start seeing `ImportError` due to missing packages, you can install them manually using
`pip` or consider if its time to switch to a *full install* with conda.

### Full Install with conda

This is the *full install* used by the *core developers*.

#### Create a development environment

Since Panel interfaces with a large range of different libraries the full test suite requires a wide range of dependencies. To make it easier to install and run different parts of the test suite across
different platforms Panel uses a library called `pyctdev` to make things more consistent and general. To start with `cd` into the panel directory and set up conda using the following commands:

```bash
cd panel
conda install -c pyviz "pyctdev>0.5.0"
```

Once pyctdev is available and you are in the cloned panel repository you can set up an environment with:

```bash
doit env_create -c pyviz/label/dev -c conda-forge --name=panel_dev --python=3.9
```

Specify the desired Python version, currently Panel officially supports Python 3.9 or later. Once the environment has been created you can activate it with:

```bash
conda activate panel_dev
```

#### Install Panel in editable mode

To perform an editable install of Panel, including all the dependencies required to run the full unit test suite, run the following:

```bash
doit develop_install -c pyviz/label/dev -c conda-forge -c bokeh -o build -o tests -o recommended
```

The above command installs Panel's dependencies using conda, then performs a pip editable install of Panel. If it fails, `nodejs>=14.0.0` may be missing from your environment, fix it with `conda install -c conda-forge nodejs` then rerun above command.

If you also want to run the UI tests you'll need to install pytest-playwright with `conda`:

``` bash
conda install pytest-playwright -c microsoft -c conda-forge
```

or with `pip` (if you prefer it, or if there's no conda package found for your platform):

``` bash
pip install pytest-playwright
```

then run:

``` bash
playwright install chromium
```

#### Enable the Jupyter extension

If you are running UI tests or intend to use the Panel Preview feature in Jupyter you must enable the server extension. To enable the classic notebook server extension:

```bash
jupyter serverextension enable panel.io.jupyter_server_extension --sys-prefix
```

For Jupyter Server:

```bash
jupyter server extension enable panel.io.jupyter_server_extension --sys-prefix
```

#### Setting up pre-commit

Panel uses [pre-commit](https://pre-commit.com/) to automatically apply linting to Panel code. If you intend to contribute to Panel we recommend you enable it with:

```bash
pre-commit install
```

This will ensure that every time you make a commit linting will automatically be applied.

#### Developing custom models

Panel ships with a number of custom Bokeh models, which have both Python and Javascript components. When developing Panel these custom models have to be compiled. This happens automatically with `SETUPTOOLS_ENABLE_FEATURES=legacy-editable pip install -e .` or `python setup.py develop`, however when running actively developing you can rebuild the extension with `panel build panel`. The `build` command is just an alias for `bokeh build`; see
the [Bokeh developer guide](https://docs.bokeh.org/en/latest/docs/dev_guide/setup.html) for more information about developing bokeh models.

Just like any other Javascript (or Typescript) library Panel defines a `package.json` and `package-lock.json` files. When adding, updating or removing a dependency in the package.json file ensure you commit the changes to the `package-lock.json` after running `npm install`.

#### Bundling resources

Panel bundles external resources required for custom models and templates into the `panel/dist` directory. The bundled resources have to be collected whenever they change, so rerun `SETUPTOOLS_ENABLE_FEATURES=legacy-editable pip install -e .` or `python setup.py develop` whenever you change one of the following:

* A new model is added with a `__javascript_raw__` declaration or an existing model is updated
* A new template with a `_resources` declaration is added or an existing template is updated
* A CSS file in one of template directories (`panel/template/*/`) is added or modified

#### Next Steps

You will likely want to check out the

- [Extensions Guide](extensions.md)
- [Testing Guide](testing.md).
- [WASM Guide](wasm.md)

## Useful Links

- [Dev version of Panel Site](https://holoviz-dev.github.io/panel)
  - Use this to explore new, not yet released features and docs
- [Panel main branch on Binder](https://mybinder.org/v2/gh/holoviz/panel/main?urlpath=lab/tree/examples)
  - Use this to quickly explore and manually test the newest panel features in a fresh environment with all requirements installed.
  - Replace `main` with `name-of-other-branch` or `version`for other branches.
    - For example https://mybinder.org/v2/gh/holoviz/panel/v1.2.1?urlpath=lab/tree/examples

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

extensions
testing
wasm
Developing custom models <Developing_Custom_Models>
```
