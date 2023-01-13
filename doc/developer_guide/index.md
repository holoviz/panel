# Developer Guide

The Panel library is a complex project which provides a wide range of data interfaces and an extensible set of plotting backends, which means the development and testing process involves a wide set of libraries.

## Preliminaries

### Git

The Panel source code is stored in a [Git](https://git-scm.com) source control repository.  The first step to working on Panel is to install Git on to your system.  There are different ways to do this depending on whether, you are using Windows, OSX, or Linux.

To install Git on any platform, refer to the [Installing Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) section of the [Pro Git Book](https://git-scm.com/book/en/v2).

### Conda

Developing Panel requires a wide range of packages that are not easily and quickly available using pip. To make this more manageable, core developers rely heavily on the [conda package manager](https://conda.io/docs/intro.html) for the free [Anaconda](https://anaconda.com/downloads) Python distribution. However, ``conda`` can also install non-Python package dependencies, which helps streamline Panel development greatly. It is *strongly* recommended that anyone developing Panel also use ``conda``, and the remainder of the instructions will assume that ``conda`` is available.

To install Conda on any platform, see the [Download conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html) section of the `conda documentation`_.

## Cloning the Repository

The source code for the Panel project is hosted on [GitHub](https://github.com/holoviz/panel). To clone the source repository, issue the following command:

```bash
git clone https://github.com/holoviz/panel.git
```

This will create a ``panel`` directory at your file system location. This ``panel`` directory is referred to as the *source checkout* for the remainder of this document.

## Create a development environment

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

Specify the desired Python version, currently Panel officially supports Python 3.7, 3.8, 3.9 and 3.10. Once the environment has been created you can activate it with:

```bash
conda activate panel_dev
```

## Install Panel in editable mode

To perform an editable install of Panel, including all the dependencies required to run the full unit test suite, run the following:

```bash
doit develop_install -c pyviz/label/dev -c conda-forge -c bokeh -o build -o tests -o recommended
```

The above command installs Panel's dependencies using conda, then performs a pip editable install of Panel. If it fails, `nodejs>=14.0.0` may be missing from your environment, fix it with `conda install -c conda-forge nodejs` then rerun above command.

If you also want to run the UI tests run the following:
``` bash
pip install playwright pytest-playwright
playwright install chromium
```

## Enable the Jupyter extension

If you are running UI tests or intend to use the Panel Preview feature in Jupyter you must enable the server extension. To enable the classic notebook server extension:

```bash
jupyter serverextension enable panel.io.jupyter_server_extension --sys-prefix
```

For Jupyter Server:

```bash
jupyter server extension enable panel.io.jupyter_server_extension --sys-prefix
```

## Setting up pre-commit

Panel uses [pre-commit](https://pre-commit.com/) to automatically apply linting to Panel code. If you intend to contribute to Panel we recommend you enable it with:

```bash
pre-commit install
```

This will ensure that every time you make a commit linting will automatically be applied.

## Developing custom models

Panel ships with a number of custom Bokeh models, which have both Python and Javascript components. When developing Panel these custom models have to be compiled. This happens automatically with `SETUPTOOLS_ENABLE_FEATURES=legacy-editable pip install -e .` or `python setup.py develop`, however when runnning actively developing you can rebuild the extension with `panel build panel`. The `build` command is just an alias for `bokeh build`; see
the [Bokeh developer guide](https://docs.bokeh.org/en/latest/docs/dev_guide/setup.html) for more information about developing bokeh models.

Just like any other Javascript (or Typescript) library Panel defines a `package.json` and `package-lock.json` files. When adding, updating or removing a dependency in the package.json file ensure you commit the changes to the `package-lock.json` after running `npm install`.

## Bundling resources

Panel bundles external resources required for custom models and templates into the `panel/dist` directory. The bundled resources have to be collected whenever they change, so rerun `SETUPTOOLS_ENABLE_FEATURES=legacy-editable pip install -e .` or `python setup.py develop` whenever you change one of the following:

* A new model is added with a `__javascript_raw__` declaration or an existing model is updated
* A new template with a `_resources` declaration is added or an existing template is updated
* A CSS file in one of template directories (`panel/template/*/`) is added or modified

## Next Steps

You will likely want to check out the :ref:`devguide_testing` guide. Meanwhile, if you have any problems with the steps here, please visit our [Discourse](https://discourse.holoviz.org/c/panel/5).

## Useful Links

- [Dev version of Panel Site](https://pyviz-dev.github.io/panel)
   - Use this to explore new, not yet released features and docs
- [Panel main branch on Binder](https://mybinder.org/v2/gh/holoviz/panel/main?urlpath=lab/tree/examples)
   - Use this to quickly explore and manually test the newest panel features in a fresh environment with all requirements installed.
   - Replace `main` with `name-of-other-branch` for other branches.

```{toctree}
:titlesonly:
:hidden:
:maxdepth: 2

testing
Developing custom models <Developing_Custom_Models>
```
