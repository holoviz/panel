# ReactiveHTML component with callback

In this guide you will learn how to add callbacks to your `ReactiveHTML` components.

## Slideshow with Python callback

This example will show you how to create a `SlideShow` component that uses a python *callback*
function to update the `SlideShow` image when its clicked:

```{pyodide}
import param
import panel as pn

from panel.reactive import ReactiveHTML

pn.extension()

class Slideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = '<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${_img_click}"></img>'

    def _img_click(self, event):
        self.index += 1

Slideshow(width=500, height=200)
```

As we can see this approach lets us quickly build custom HTML components with complex interactivity.
However if we do not need any complex computations in Python we can also construct a pure JS equivalent:

## Slideshow with Javascript Callback

This example will show you how to create a `SlideShow` component that uses a Javascript *callback*
function to update the `SlideShow` image when its clicked:

```{pyodide}
import param
import panel as pn

from panel.reactive import ReactiveHTML

pn.extension()

class JSSlideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = """<img id="slideshow" src="https://picsum.photos/800/300?image=${index}" onclick="${script('click')}"></img>"""

    _scripts = {'click': 'data.index += 1'}

JSSlideshow(width=800, height=300)
```

By using Javascript callbacks instead of Python callbacks you can achieve higher performance,
components that can be *js linked* and components that will also work when your app is saved to
static html.
