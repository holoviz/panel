# Developing Panel

Panel consists of both Python and TypeScript components, which means in certain circumstances extra build steps are required when developing Panel. As described in the [developer setup guide](index.md) you can easily set up a development environment using `hatch`. The remaining instructions assume you have set up the development environment and are working from within an environment shell.

## Developing TypeScript

### Building

When you add or modify one of the models in `panel/models` you have to rebuild the panel.js file. From within the environment and the root of the project you can run:

```bash
panel build panel
```

This will re-compile `panel.js` and `panel.min.js` in the `panel/dist` directory.

### Modifying dependencies

Just like any other Javascript (or Typescript) library Panel defines a `package.json` and `package-lock.json` files located in the `panel/` directory. When adding, updating or removing a dependency in the package.json file ensure you commit the changes to the `package-lock.json` after running `panel build panel`.

## Bundling resources

Panel bundles external resources required for custom models, themes and templates into the `panel/dist` directory. This is necessary when you modify any of the following:

* A new model is added with a `__javascript__` or `__css__` declaration or an existing model is modified.
* A new template, design or theme with a `_resources` declaration is added or an existing template, design or theme is modified
* A CSS or JS file in one of template or theme directories (`panel/template/*/` and `panel/theme/*`) is added or modified.

To run the bundling step execute:

```bash
panel bundle --all --verbose
```

This will re-download all external resources and bundle (and potentially minify) local resources. If you have only modified a specific component you can instead bundle one or more of `--models`, `--themes` or `--templates`. If you haven't modified any external resources you can also skip external resources by providing the `--only-local` option.
