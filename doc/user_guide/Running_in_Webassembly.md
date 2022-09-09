# Running in Webassembly

Panel lets you write dashboards and other applications in Python that are accessed using a web browser. Typically, the Python interpreter runs as a separate Jupyter or Bokeh server process, communicating with JavaScript code running in the client browser. However, it is now (as of 2022) possible to run Python directly in the browser, with no separate server needed!

The underlying technology involved is called [WebAssembly](https://webassembly.org/) (or WASM). More specifically, [Pyodide](https://pyodide.org/) pioneered the ability to install Python libraries, manipulate the web page's [DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model/Introduction) from Python, and execute regular Python code entirely in the browser. A number of libraries have sprung up around Python in WASM, including [PyScript](https://pyscript.net/).

Panel can be run directly in Pyodide and has special support for rendering in PyScript. This guide will take us through the process of installing Panel in the browser, using it to render individual components or export entire applications to run as pure client applications, with no server at all (just like JavaScript).

## Installing Panel in the browser

To install Panel in the browser you merely have to use the installation mechanism provided by each supported runtime:

### Pyodide

Currently the best supported mechanism for installing packages in Pyodide is `micropip`, which can be imported within the Pyodide runtime. Once imported simple use `micropip.install`:

```python
import micropip
micropip.install('panel')
```

To get started with Pyodide simply follow their [Getting started guide](https://pyodide.org/en/stable/usage/quickstart.html). Note that if you want to render Panel output you will also have to load Bokeh.js and Panel.js from CDN. The most basic pyodide application therefore looks like this:

```html
<!DOCTYPE html>
<html>
  <head>
    <script src="https://cdn.jsdelivr.net/pyodide/v0.21.2/full/pyodide.js"></script>

    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-2.4.3.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.4.3.min.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.4.3.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@holoviz/panel@0.14.0/dist/panel.min.js"></script>

  </head>
  <body>
    <script type="text/javascript">
      async function main(){
        let pyodide = await loadPyodide();
        pyodide.runPython(`
            import micropip
            micropip.install('panel')

            import panel as pn
            ...
        `);
      }
      main();
    </script>
  </body>
</html>
```

### PyScript

PyScript makes it even easier to manage your dependencies, with a `<py-env>` HTML tag. Simply include `panel` in the list of dependencies and PyScript will install it automatically:

```html
<py-env>
- panel
...
</py-env>
```

Once installed you will be able to `import panel` in your `<py-script>` tag. Again, make sure you also load Bokeh.js and Panel.js:


```html
<html>
  <head>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-2.4.3.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-2.4.3.min.js"></script>
    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-2.4.3.min.js"></script>
    <script type="text/javascript" src="https://cdn.jsdelivr.net/npm/@holoviz/panel@0.14.0/dist/panel.min.js"></script>

    <link rel="stylesheet" href="https://pyscript.net/stable/pyscript.css" />
    <script defer src="https://pyscript.net/stable/pyscript.js"></script>

  </head>
  <body>
    <py-env>
      - panel
      ...
    </py-env>
    <py-script>
      import panel as pn
      ...
    </py-script>
  </body>
</html>
```

## Rendering Panel components

Rendering Panel components into the DOM is quite straightforward. You can simply use the `.servable()` method on any component and provide a target that should match the `id` of a DOM node:

```python
import panel as pn

slider = pn.widgets.FloatSlider(start=0, end=10, name='Amplitude')

def callback(new):
    return f'Amplitude is: {new}'

pn.Row(slider, pn.bind(callback, slider)).servable(target='simple_app');
```

This code will render this simple application into the `simple_app` DOM node:

```python
<div id="simple_app"></div>
```

Alternatively you can also use the `panel.io.pyodide.write` function to write into a particular DOM node:

```python
await pn.io.pyodide.write('simple_app', component)
```

### PyScript

Current versions of PyScript will automatically render the output of the last cell of a <py-script> tag. E.g. in this example the `pn.Row()` component will be rendered wherever you placed the tag:

```html
<py-script>
  import panel as pn

  slider = pn.widgets.FloatSlider(start=0, end=10, name='Amplitude')

  def callback(new):
      return f'Amplitude is: {new}'

  pn.Row(slider, pn.bind(callback, slider))
</py-script>
```

## Converting Panel applications

Writing an HTML file from scratch with all the Javascript and Python dependencies and other boilerplate can be quite annoying, and requires learning a good bit of HTML. To avoid writing all the boilerplate, Panel provides support for converting an entire application (including Panel templates) to an HTML file, using the `panel convert` API. As a starting point create one or more Python scripts or notebook files containing your application. The only requirement is that they import only global modules (relative imports of other scripts or modules is not supported).

The ``panel convert`` command has the following options:

    positional arguments:
      SCRIPTs               The scripts or notebooks to convert

    optional arguments:
      -h, --help            Show this help message and exit
      --to                  The format to convert to, one of 'pyodide', 'pyodide-worker' or 'pyscript'
      --out                 Directory to export files to
      --title               Custom title for the application(s)
      --prerender           Whether to export pre-rendered models to display while pyodide loads.
      --index               Whether to create an index if multiple files are served.
      --pwa                 Whether to add files to allow serving the application as a Progressive Web App.
      --requirements        Explicit list of Python requirements to add to the converted file.

### Formats

Using the `--to` argument on the CLI you can control the format of the file that is generated by `panel convert`. You have three options, each with distinct advantages and disadvantages:

- **`pyodide`** (default): Run application using Pyodide running in the main thread. This option is less performant than pyodide-worker but produces completely standalone HTML files that do not have to be hosted on a static file server.
- **`pyodide-worker`**: Generates an HTML file and a JS file containing a Web Worker that runs in a separate thread. This is the most performant option, but files have to be hosted on a static file server.
- **`pyscript`**: Generates an HTML leveraging PyScript. This produces standalone HTML files containing `<py-env>` and `<py-script>` tags containing the dependencies and the application code. This output is the most readable, and should have equivalent performance to the `pyodide` option.

### Progressive Web Apps

Progressive web applications (PWAs) provide a way for your web apps to behave almost like a native application, both on mobile devices and on the desktop. The `panel convert` CLI has a `--pwa` option that will generate the necessary files to turn your Panel + Pyodide application into a PWA. The web manifest, service worker script and assets such as thumbnails are exported alongside the other HTML and JS files and can then be hosted on your static file host. Note that Progressive web apps must be served via HTTPS to ensure user privacy, security, and content authenticity, including the application itself and all resources it references. Depending on your hosting service, you will have to enable HTTPS yourself. GitHub pages generally make this very simple and provide a great starting point.

Once generated, you can inspect the `site.webmanifest` file and modify it to your liking, including updating the favicons in the assets directory.

### Index

By default if you convert multiple applications, Panel will automatically create an index page for you that allows you to navigate between the applications.

### Prerender

The `--prerender` option greatly improves the loading experience for a user. One major drawback of Pyodide at the moment is that it actually has to fetch the entire Python runtime and all required packages from a CDN. This can be **very** slow depending on your internet connection. The `prerender` option renders the application using the current Python process (presumably outside the browser) into the HTML file as a "cached" copy of the application for the user to see while the Python runtime is initialized and the actual browser-generated application is ready for interaction.
