# ReactiveHTML component with callback

In this guide we will show you how to add callbacks to your `ReactiveHTML` components.

## Slideshow with Python callback

This example shows you how to create a `Slideshow` component that uses a Python *callback* function to update the `Slideshow` image when its clicked:

```python
import param
import panel as pn

from panel.reactive import ReactiveHTML

pn.extension()

class Slideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = ''

    def _img_click(self, event):
        self.index += 1

Slideshow().servable()
```

This approach lets you quickly build custom HTML components with complex interactivity. However if you do not need any complex computations in Python you can also construct a pure JS equivalent:

## Slideshow with Javascript Callback

This example shows you how to create a `Slideshow` component that uses a Javascript *callback* function to update the `Slideshow` image when its clicked:

```python
import param
import panel as pn

from panel.reactive import ReactiveHTML

pn.extension()

class JSSlideshow(ReactiveHTML):

    index = param.Integer(default=0)

    _template = """"""

    _scripts = {'click': 'data.index += 1'}

JSSlideshow().servable()
```

By using Javascript callbacks instead of Python callbacks you can achieve higher performance, components that can be *js linked* and components that will also work when your app is saved to static html.
