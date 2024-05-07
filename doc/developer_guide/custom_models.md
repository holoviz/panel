# Developing custom models

Panel ships with a number of custom Bokeh models, which have both Python and Javascript components.
When developing Panel these custom models have to be compiled.
This happens automatically with `pip install -e .` or `pixi run install`, however when running actively developing you can rebuild the extension with `panel build panel` from the source directory. The `build` command is just an alias for `bokeh build`; see
the [Bokeh developer guide](https://docs.bokeh.org/en/latest/docs/dev_guide/setup.html) for more information about developing bokeh models.

Just like any other Javascript (or Typescript) library Panel defines a `package.json` and `package-lock.json` files.
When adding, updating or removing a dependency in the package.json file ensure you commit the changes to the `package-lock.json` after running `npm install`.

# Bundling resources

Panel bundles external resources required for custom models and templates into the `panel/dist` directory.
The bundled resources have to be collected whenever they change, so rerun `pip install -e .` or `pixi run install`, whenever you change one of the following:

- A new model is added with a `__javascript_raw__` declaration or an existing model is updated
- A new template with a `_resources` declaration is added or an existing template is updated
- A CSS file in one of template directories (`panel/template/*/`) is added or modified
