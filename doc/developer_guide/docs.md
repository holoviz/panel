# Documentation

The Panel documentation consists of many different types of content and many of the examples have complicated dependencies. At a high-level the documentation is built using [Sphinx](https://www.sphinx-doc.org/en/master/), [MyST](https://myst-parser.readthedocs.io/en/latest/) and [nbsite](https://github.com/pyviz-dev/nbsite). The main content is one of the following:

- Notebooks: Many Panel examples are written as notebooks which are converted into documentation using `nbsite` and `MyST`.
- Markdown: Panel documentation is primarily written using MyST flavored markdown.
- Pyodide: A lot of the materials can be executed live on the website using the `pyodide` directive.
- API docs: The API docs are auto-generated during the build stage.

## Building docs

Unlike the regular development workflow we recommend using the `doc` environment directly to achieve isolation. To build the entire documentation run the following three commands:

```bash
hatch run docs:generate-rst
hatch run docs:refmanual
hatch run docs:build
```

Once built you can view it with:

```bash
hatch run docs:serve
```

and navigate to `http://localhost:8000` in your browser.

## Building Pyodide Gallery

Panel also generates a gallery of examples using `pyodide`. This can be built with:

```bash
hatch run docs:build-pyodide
```
