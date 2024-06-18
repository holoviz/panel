# ESM component with callback

In this guide we will show you how to add callbacks to your ESM components.

## Slideshow with Python callback

This example shows you how to create a `SlideShow` component that uses a Python *callback* function to update the `Slideshow` image when its clicked:

```{pyodide}
import param
import panel as pn

from panel.custom import JSComponent

pn.extension()

class Slideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      const img = document.createElement('img')
      img.src = `https://picsum.photos/800/300?image=${model.index}`
      img.addEventListener('click', (event) => model.send_event('click', event))
      model.watch(() => {
        img.src = `https://picsum.photos/800/300?image=${model.index}`
      }, 'index')
      return img
    }
    """

    def _handle_click(self, event):
        self.index += 1

Slideshow(width=500, height=200).servable()
```

This approach lets you quickly build custom components with complex interactivity. However if you do not need any complex computations in Python you can also construct a pure JS equivalent:

## Slideshow with Javascript Callback

This example shows you how to create a `Slideshow` component that uses a Javascript *callback* function to update the `Slideshow` image when its clicked:

```{pyodide}
import param
import panel as pn

from panel.esm import JSComponent

pn.extension()

class JSSlideshow(JSComponent):

    index = param.Integer(default=0)

    _esm = """
    export function render({ model }) {
      const img = document.createElement('img')
      img.src = `https://picsum.photos/800/300?image=${model.index}`
      img.addEventListener('click', (event) => {
        model.index += 1
        img.src = `https://picsum.photos/800/300?image=${model.index}`
      })
      model.watch(() => {

      }, 'index')
      return img
    }
    """

JSSlideshow(width=800, height=300).servable()
```

By using Javascript callbacks instead of Python callbacks you can achieve higher performance, components that can be *js linked* and components that will also work when your app is saved to static html.
