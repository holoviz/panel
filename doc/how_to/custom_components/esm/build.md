# Handling of external resources

The ESM components make it possible to load external libraries from NPM or GitHub easily using one of two approaches:

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

```
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

## Bundling

Importing libraries directly from a CDN allows for extremely quick iteration but also means that the users of your components will have to have access to the internet to fetch the required modules. By bundling the component resources you can ship a self-contained module that includes all the dependencies, while also ensuring that you only fetch the parts of the libraries that are actually needed.

### Tooling

The tooling we recommend to bundle your component resources include `esbuild` and `npm`, both can conveniently be installed with `conda`:

```bash
conda install esbuild npm
```

### Configuration

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

    _esm = 'confetti.bundled.js'

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

Once you have set up these three files you have to install the packages with `npm`:

```bash
npm install
```

This will fetch the packages and install them into the local `node_modules` directory. Once that is complete we can run the bundling:

```bash
esbuild confetti.js --bundle --format=esm --minify --outfile=confetti.bundled.js
```

This will create a new file called `confetti.bundled.js`, which includes all the dependencies (even CSS, image files and other static assets if you have imported them).

The only thing left to do now is to update the `_esm` declaration to point to the new bundled file:

```python
class ConfettiButton(JSComponent):

    _esm = 'confetti.bundled.js'
```
