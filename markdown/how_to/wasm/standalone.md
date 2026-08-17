# Using Panel in Pyodide & PyScript

## Pyodide

### Creating a Basic Panel Pyodide Application

Create a file called **script.html** with the following content:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    
    
    
    
    
  </head>
  <body>
    
    
  </body>
</html>
```

Serve the app with:

```bash
python -m http.server
```

Open the app in your browser at [http://localhost:8000/script.html](http://localhost:8000/script.html).

The app should look like this:

![Panel Pyodide App](../../_static/images/pyodide_app_simple.png)

The default Bokeh and Panel packages are very large. Therefore we recommend installing specialized wheels:

```javascript
const bk_whl = "https://cdn.holoviz.org/panel/wheels/bokeh-{{BOKEH_VERSION}}-py3-none-any.whl";
const pn_whl = "https://cdn.holoviz.org/panel/wheels/panel-{{PANEL_VERSION}}-py3-none-any.whl";
await micropip.install(bk_whl, pn_whl);
```

:::

## PyScript

### Creating a Basic Panel PyScript Application

Create a file called **script.html** with the following content:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    
    
    
    
    <link rel="stylesheet" href="https://pyscript.net/releases/{{PYSCRIPT_VERSION}}/core.css">
    
  </head>
  <body>
    
    
  </body>
</html>
```

Serve the app with:

```bash
python -m http.server
```

Open the app in your browser at [http://localhost:8000/script.html](http://localhost:8000/script.html).

The app should look like this:

![Panel Pyodide App](../../_static/images/pyodide_app_simple.png)

The [PyScript](https://docs.pyscript.net) documentation recommends separating your configuration and Python code into different files. Examples can be found in the [PyScript Examples Gallery](https://pyscript.com/@examples?q=panel).

### Creating a Basic `py-editor` Example

Create a file called **script.html** with the following content:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    
    
    
    
    

    <link rel="stylesheet" href="https://pyscript.net/releases/{{PYSCRIPT_VERSION}}/core.css">
    
  </head>
  <body>
    
    
  </body>
</html>
```

Create a file called **mini-coi.js** with the content from [mini-coi.js](https://github.com/WebReflection/mini-coi/blob/main/mini-coi.js).

Serve the app with:

```bash
python -m http.server
```

Open the app in your browser at [http://localhost:8000/script.html](http://localhost:8000/script.html).

Click the green *run* button that appears when you hover over the lower-right corner of the editor to see the application.

:::note
In the example, we included **mini-coi.js**. This is not necessary if the [appropriate HTTP headers](https://docs.pyscript.net/2024.7.1/user-guide/workers/) are set on your server, such as on [pyscript.com](https://pyscript.com) or in Github pages.
:::

## Rendering Panel Components in Pyodide or PyScript

Rendering Panel components into the DOM is straightforward. Use the `.servable()` method on any component and provide a target that matches the `id` of a DOM node:

```python
import panel as pn

slider = pn.widgets.FloatSlider(start=0, end=10, label='Amplitude')

def callback(new):
    return f'Amplitude is: {new}'

pn.Row(slider, pn.bind(callback, slider)).servable(target='simple_app')
```

This code will render the application into the `simple_app` DOM node:

```html

```

Alternatively, you can use the `panel.io.pyodide.write` function to write into a specific DOM node:

```python
await pn.io.pyodide.write('simple_app', component)
```
