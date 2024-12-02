# Compile and Bundle ESM Components

The ESM components make it possible to load external libraries from a CDN, NPM or GitHub using one of two approaches:

1. Directly importing from `esm.sh` or another CDN or by defining a so called importmap.
2. Bundling the resources using `npm` and `esbuild`.

In this guide we will cover how and when to use each of these approaches.

## Imports

So called [ECMA script modules](https://en.wikipedia.org/wiki/ECMAScript#6th_Edition_%E2%80%93_ECMAScript_2015) or ESM modules for short, made it much simpler to build reusable modules that could easily import other libraries. Specifically they introduced `import` and `export` specifiers, which allow developers to import other libraries and export specific functions, objects and classes for the consumption of others.

These imports can reference modules directly on some CDN or you can define a so called [`importmap`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/script/type/importmap), which allows you to specify where to load a library from. Let's start with a simple example, we are going to build a `ConfettiButton`.

### Inline Imports

Let us first specify the Python portion of our component, we are simply going to create a `JSComponent` that loads `confetti.js`:

```python
import panel as pn

from panel.custom import JSComponent

pn.extension()

class ConfettiButton(JSComponent):

    _esm = 'confetti.js'

ConfettiButton().servable()
```

Now that we have our Python component let's build the Javascript (or TypeScript if you like):

```javascript
/* confetti.js */
import confetti from "https://esm.sh/canvas-confetti@1.6.0";

export function render() {
  const button = document.createElement('button')
  button.addEventListener('click', () => confetti())
  button.append('Click me!')
  return button
}
```

Here we are importing the library directly from [esm.sh](https://esm.sh/), a fast and reliable CDN to fetch libraries compiled as modern ESM bundles from.

:::{note}
esm.sh is very powerful and has many options for specifying shared dependencies or bundling dependencies together. Make sure to [check out the docs](https://esm.sh/#docs).
:::

### Import Maps

Once you move past initial development we recommend making use of import maps. To quote MDN:

> An import map is a JSON object that allows developers to control how the browser resolves module specifiers when importing JavaScript modules. It provides a mapping between the text used as the module specifier in an import statement or import() operator, and the corresponding value that will replace the text when resolving the specifier.

The import map can be declared directly on the `JSComponent` using the `_importmap` attribute. A minimum it must contain some imports:

```python
class ConfettiButton(JSComponent):

    _importmap = {
        "imports": {
            "canvas-confetti": "https://esm.sh/canvas-confetti@1.6.0",
        }
    }

    _esm = 'confetti.js'
```

Now that we have separately declared the import we can update the `import` line in the `confetti.js` file:

```javascript
/* confetti.js */
import confetti from "canvas-confetti";
```

This approach cleanly separates the definitions of the libraries and their versions from the actual code. If you are only importing a single library this is generally all you need to do, however once you have multiple inter-connected dependencies you may have to go beyond this.

Let's say for instance you want to import libraries `A`, `B` and `C`. Both `B` and `C` depend on `A`, however because esm.sh rewrites imports you may end up with multiple different versions `A`.

In order to avoid this we can ask `esm.sh` not to rewrite the imports using the `external` query parameter. This tells esm.sh that `A` will be provided externally (i.e. by us), ensuring that libraries `B` and `C` both import the version of `A` we declare:

```python
{
  "imports": {
    "A": "https://esm.sh/A@1.0.0",
    "B": "https://esm.sh/B?external=A",
    "C": "https://esm.sh/C?external=A",
  }
}
```

To give a real world example that esm.sh itself provides:

```
{
  "imports": {
    "preact": "https://esm.sh/preact@10.7.2",
    "preact-render-to-string": "https://esm.sh/preact-render-to-string@5.2.0?external=preact"
  }
}
```
:::{note}
Import maps supports trailing slash that can not work with URL search params friendly. To fix this issue, esm.sh provides a special format for import URL that allows you to use query params with trailing slash: change the query prefix ? to & and put it after the package version.

```
{
  "imports": {
    "react-dom": "https://esm.sh/react-dom@18.2.0?pin=v135&dev",
    "react-dom/": "https://esm.sh/react-dom@18.2.0&pin=v135&dev/"
  }
}
```
:::

## Compile & Bundling

Importing libraries directly from a CDN allows for quick experimentation and iteration but also means that the users of your components will have to have access to the internet to fetch the required modules. By compiling and bundling the component and external resources you can ship a self-contained and optimized ESM module that includes all the dependencies, while also ensuring that you only fetch the parts of the libraries that are actually needed. The `panel compile` command provides a simple entrypoint to compile one or more components into a single component.

### Setup

The compilation and bundling workflow depends on two JavaScript tools: `node.js` (or more specifically the node package manager `npm`) and `esbuild`. The most convenient way to install them is `conda` but you can also set up your own node environment using something like [`asdf`](https://asdf-vm.com/guide/getting-started.html), [`nvm`](https://github.com/nvm-sh/nvm?tab=readme-ov-file#installing-and-updating) or [`volta`](https://volta.sh/).

::::{tab-set}

:::{tab-item} `conda`
```bash
conda install esbuild npm
```
:::

:::{tab-item} Custom Node.js installation

Once you have set up `node.js` you can install `esbuild` globally with:

```bash
npm install -g esbuild
```

and confirm the installation with:

```bash
esbuild --version
```
:::

::::

### Panel Compile Command

Panel provides the `panel compile` command to automate the compilation of ESM components from the command line and bundle their resources. This functionality requires `npm` and `esbuild` to be installed globally on your system.

#### Example Usage

Let's consider a confetti.py module containing a custom JavaScript component:

```python
# confetti.py
import panel as pn

from panel.custom import JSComponent

class ConfettiButton(JSComponent):

    _esm = """
import confetti from "https://esm.sh/canvas-confetti@1.6.0";

export function render() {
  const button = document.createElement('button')
  button.addEventListener('click', () => confetti())
  button.append('Click me!')
  return button
}"""
```

To compile this component, you can use the following command:

```bash
panel compile confetti
```

:::{hint}
`panel compile` accepts file paths, e.g. `my_components/custom.py`, or dotted module names, e.g. `my_package.custom`. If you provide a module name it must be importable.
:::

This will automatically discover the `ConfettiButton` but you can also explicitly request a single component by adding the class name:

```bash
panel compile confetti:ConfettiButton
```

After running the command you should output that looks a like this, indicating the build succeeded:

```bash
Running command: npm install

npm output:

added 1 package, and audited 2 packages in 649ms

1 package is looking for funding
  run `npm fund` for details

found 0 vulnerabilities

Running command: esbuild /var/folders/7c/ww31pmxj2j18w_mn_qy52gdh0000gq/T/tmp9yhyqo55/index.js --bundle --format=esm --outfile=<module-path>/ConfettiButton.bundle.js --minify

esbuild output:

  .....<module-path>/ConfettiButton.bundle.js  10.5kb

⚡ Done in 9ms
```

If the supplied module or package contains multiple components they will all be bundled together by default. If instead you want to generate bundles for each file explicitly you must list them with the `:` syntax, e.g. `panel compile package.module:Component1,Component2`. You may also provide a glob pattern to request multiple components to be built individually without listing them all out, e.g. `panel compile "package.module:Component*"`.

During runtime the compiled bundles will be resolved automatically, where bundles compiled for a specific component (i.e. `<component-name>.bundle.js`) take highest precedence and we then search for module bundles up to the root package, e.g. for a component that lives in `package.module` we first search for `package.module.bundle.js` in the same directory as the component and then recursively search in parent directories until we reach the root of the package.

If you rename the component or modify its code or `_importmap`, you must recompile the component. For ongoing development, consider using the `--dev` option to ignore the compiled file and automatically reload the development version when it changes.

#### Compilation Steps

The `panel compile` command performs the compilation and bundling in several steps:

1. **Identify Components**: The first step is to discover the components in the provided module(s).
2. **Extract External Dependencies**: The command identifies external dependencies from the `_importmap` (if defined) or directly from the ESM code. These dependencies are written to a `package.json` file in a temporary build directory. The `.js(x)` files corresponding to each component are also placed in this directory.
3. **Install Dependencies**: The command runs `npm install` within the build directory to fetch all external dependencies specified in `package.json`.
4. **Bundle and Minify**: The command executes `esbuild index.js --bundle --format=esm --minify --outfile=<module-path>ConfettiButton.bundle.js` to bundle the ESM code into a single minified JavaScript file.
5. **Output the Compiled Bundle(s)**: The final output is one or more compiled JavaScript bundle (`ConfettiButton.bundle.js`).

#### Compiling Multiple Components

If you intend to ship multiple components with shared dependencies, `panel compile` can generate a combined bundle, which ensures that the dependencies are only loaded once. By default it will generate one bundle per module or per component, but if you declare a `_bundle` attribute on the class, declared either as a string defining a relative path or a `pathlib.Path`, you can generate shared bundles across modules. These bundles can include as many components as needed and will be automatically loaded when you use the component.

As an example, imagine you have a components declared across your package containing two distinct components. By declaring a path that resolves to the same location we can bundle them together:

```python
# my_package/my_module.py
class ComponentA(JSComponent):
    _bundle = './dist/custom.bundle.js'

# my_package/subpackage/other_module.py
class ComponentB(JSComponent):
    _bundle = '../dist/custom.bundle.js'
```

when you compile it with:

```bash
panel compile my_package.my_module my_package.subpackage.other_module
```

you will end up with a single `custom.bundle.js` file placed in the `my_package/dist` directory.

(build-dir)=
#### Using the `--build-dir` Option

The `--build-dir` option allows you to specify a custom directory where the `package.json` and raw JavaScript/JSX modules will be written. This is useful if you need to manually modify the dependencies before the bundling process and/or debug issues while bundling. To use this feature, follow these steps:

1. Run the compile command with the `--build-dir` option to generate the directory:

```bash
panel compile confetti.py --build-dir ./custom_build_dir
```

2. Navigate to the specified build directory and manually edit the `package.json` file to adjust dependencies as needed.

3. Once you've made your changes, you can manually run the `esbuild` command:

```bash
esbuild custom_build_dir/index.js --format=esm --bundle --minify
```

Here is a typical structure of the build_dir directory:

```
custom_build_dir/
├── index.js
├── package.json
├── <Component>.js
└── <OtherComponent>.js
```

The compiled JS file will now be loaded automatically as long as it remains alongside the component. If you rename the component you will have to delete and recompile the JS file. If you make changes to the code or `_importmap` you also have to recompile. During development we recommend using `--dev`, which ignores the compiled file.

```{caution}
The `panel compile` CLI tool is still very new and experimental. In our testing it was able to compile and bundle most components but there are bound to be corner cases.

We will continue to improve the tool and eventually allow you to bundle multiple components into a single bundle to allow sharing of resources.
```

### React Components

React components automatically include `react` and `react-dom` in their bundles. The version of `React` that is loaded can be specified the `_react_version` attribute on the component class. We strongly suggest you pin a specific version on your component to ensure your component does not break should the version be bumped in Panel.

### Manual Compilation

If you have more complex requirements or the automatic compilation fails for whatever reason you can also manually compile the output. We generally strongly recommend that you start by generating the initial bundle structure by providing a `--build-dir` and then tweaking the resulting output.

#### Configuration

To run the bundling we will need one additional file, the `package.json`, which, just like the import maps, determines the required packages and their versions. The `package.json` is a complex file with tons of configuration options but all we will need are the [dependencies](https://docs.npmjs.com/cli/v10/configuring-npm/package-json#dependencies).

To recap here are the three files that we need:

::::{tab-set}

:::{tab-item} package.json

```json
{
  "name": "confetti-button",
  "dependencies": {
    "canvas-confetti": "^1.6.0"
  }
}
```
:::

:::{tab-item} confetti.py

``` python
import panel as pn

from panel.custom import JSComponent

pn.extension()

class ConfettiButton(JSComponent):

    _esm = 'confetti.js'

ConfettiButton().servable()
```
:::


:::{tab-item} confetti.js
``` javascript
import confetti from "canvas-confetti";

export function render() {
  const button = document.createElement('button')
  button.addEventListener('click', () => confetti())
  button.append('Click me!')
  return button
}
:::

::::

#### Build

Once you have set up these three files you have to install the packages with `npm`:

```bash
npm install
```

This will fetch the packages and install them into the local `node_modules` directory. Once that is complete we can run the bundling:

```bash
esbuild confetti.js --bundle --format=esm --minify --outfile=ConfettiButton.bundle.js
```

This will create a new file called `ConfettiButton.bundle.js`, which includes all the dependencies (even CSS, image files and other static assets if you have imported them).


#### Complex Bundles

If you want to bundle multiple components into a singular bundle and do not want to leverage the built-in compilation you can make do without specifying the `_esm` class variable entirely and always load the bundle directly. If you organize your Javascript/TypeScript/React code in the same way as described in the [--build-dir](#build-dir) section you can have a manual compilation workflow with all the benefits of automatic reload.

As an example let's say you have a module with multiple components:

```
panel_custom/
├── build/
    ├── index.js
    ├── package.json
    ├── <Component>.js<x>
    └── <OtherComponent>.js<x>
├── __init__.py
├── components.py
```

Ensure that the `index.js` file exports each component:

::::{tab-set}

:::{tab-item} `JSComponent`
```javascript
import * as Component from "./Component"
import * as OtherComponent from "./OtherComponent"
export default {Component, OtherComponent}
```
:::

:::{tab-item} `ReactComponent`
A `ReactComponent` library MUST also export `React` and `createRoot`:

```javascript
import * as Component from "./Component"
import * as OtherComponent from "./OtherComponent"
import * as React from "react"
import {createRoot} from "react-dom/client"
export default {Component, OtherComponent, React, createRoot}
```
:::

::::

You can now develop your JS components as if it were a normal JS library. During the build step you would then run:

```bash
esbuild panel-custom/build/index.js --bundle --format=esm --minify --outfile=panel_custom/panel_custom.components.bundle.js
```

or replace `panel_custom.components.bundle.js` with the path specified on your component's `_bundle` attribute.
