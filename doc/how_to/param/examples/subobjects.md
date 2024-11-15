# Param Subobjects

```{pyodide}
import panel as pn
import param
import numpy as np

pn.extension(template='bootstrap')
```

This example demonstrates how to use the Param library to express nested hierarchies of classes whose parameters can be edited in a GUI, without tying those classes to Panel or any other GUI framework.

For this purpose we create a hierarchy of three classes that draw Bokeh plots. At the top level there is a ``ShapeViewer`` that allows selecting between different ``Shape`` classes. The Shape classes include a subobject controlling the ``Style`` (i.e. the `color` and `line_width`) of the drawn shapes.

In each case, `param.depends` is used to indicate which parameter that computation depends on, either a parameter of this object (as for  `radius` below) or a parameter of a subobject (i.e., a parameter of one of this object's parameters, as for `style.color` below).

```{pyodide}
from bokeh.plotting import figure

class Style(param.Parameterized):

    color = param.Color(default='#0f6f0f')

    line_width = param.Number(default=2, bounds=(0, 10))


class Shape(param.Parameterized):

    radius = param.Number(default=1, bounds=(0, 1))

    style = param.Parameter(precedence=3)

    def __init__(self, **params):
        if 'style' not in params:
            params['style'] = Style(name='Style')
        super(Shape, self).__init__(**params)
        self.figure = figure(x_range=(-1, 1), y_range=(-1, 1), sizing_mode="stretch_width", height=400)
        self.renderer = self.figure.line(*self._get_coords())
        self._update_style()

    @param.depends('style.color', 'style.line_width', watch=True)
    def _update_style(self):
        self.renderer.glyph.line_color = self.style.color
        self.renderer.glyph.line_width = self.style.line_width

    def _get_coords(self):
        return [], []

    def view(self):
        return self.figure


class Circle(Shape):

    n = param.Integer(default=100, precedence=-1)

    def _get_coords(self):
        angles = np.linspace(0, 2*np.pi, self.n+1)
        return (self.radius*np.sin(angles),
                self.radius*np.cos(angles))

    @param.depends('radius', watch=True)
    def update(self):
        xs, ys = self._get_coords()
        self.renderer.data_source.data.update({'x': xs, 'y': ys})

class NGon(Circle):

    n = param.Integer(default=3, bounds=(3, 10), precedence=1)

    @param.depends('radius', 'n', watch=True)
    def update(self):
        xs, ys = self._get_coords()
        self.renderer.data_source.data.update({'x': xs, 'y': ys})


shapes = [NGon(name='NGon'), Circle(name='Circle')]
```

Having defined our basic domain model (of shapes in this case), we can now make a generic viewer using Panel without requiring or encoding information about the underlying domain objects.  Here, we define a `view` method that will be called whenever any of the possible parameters that a shape might have changes, without necessarily knowing what those are (as for `shape.param` below). That way, if someone adds a `Line` shape that has no `n` parameter but has `orientation`, the viewer should continue to work and be responsive. We can also depend on specific parameters (as for `shape.radius`) if we wish. Either way, the panel should then reactively update to each of the shape's parameters as they are changed in the browser:

```{pyodide}
class ShapeViewer(param.Parameterized):

    shape = param.Selector(default=shapes[0], objects=shapes)

    @param.depends('shape', 'shape.param')
    def view(self):
        return self.shape.view()

    @param.depends('shape', 'shape.radius')
    def title(self):
        return '## %s (radius=%.1f)' % (type(self.shape).__name__, self.shape.radius)

    def panel(self):
        return pn.Column(self.title, self.view, sizing_mode="stretch_width")


# Instantiate and display ShapeViewer
viewer = ShapeViewer()
subpanel = pn.Column()

pn.Row(
    pn.Column(pn.Param(viewer.param, expand_layout=subpanel, name="Shape Settings"), subpanel),
    viewer.panel(),
).servable()
```
