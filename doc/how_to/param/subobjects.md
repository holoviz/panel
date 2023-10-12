# Create nested UIs

This guide addresses how to structure `Parameterized` classes with subobjects to create nested UIs automatically.

```{admonition} Prerequisites
1. The [How to > Generate Widgets from Parameters](./uis.md) guide demonstrates the generation of widgets.
2. The [How to > ](./dependencies.md) guide demonstrates how to use `@param.depends` to express dependencies between parameters and functions.

```

---

``Parameterized`` objects often have parameter values which are themselves ``Parameterized`` objects, forming a tree-like structure. Panel allows you to edit not just the main object's parameters but also lets you drill down to the subobject. Let us first define some classes declaring a hierarchy of Shape classes which draw a Bokeh plot of the selected shape:

```{pyodide}
import numpy as np
import panel as pn
import param

from bokeh.plotting import figure

pn.extension()

class Shape(param.Parameterized):

    radius = param.Number(default=1, bounds=(0, 1))

    def __init__(self, **params):
        super(Shape, self).__init__(**params)
        self.figure = figure(x_range=(-1, 1), y_range=(-1, 1))
        self.renderer = self.figure.line(*self._get_coords())

    def _get_coords(self):
        return [], []

    def view(self):
        return self.figure


class Circle(Shape):

    n = param.Integer(default=100, precedence=-1)

    def _get_coords(self):
        angles = np.linspace(0, 2 * np.pi, self.n + 1)
        return (self.radius * np.sin(angles),
                self.radius * np.cos(angles))

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
```

Now that we have multiple Shape classes we can make instances of them and declare a ``ShapeViewer`` to select between them. We can also declare two methods with parameter dependencies, updating the plot and the plot title. The important thing to note here is that the ``param.depends`` decorator can not only depend on parameters on the object itself but also on specific parameters on the subobject, e.g. ``shape.radius``, or on all parameters of the subobject, expressed as ``shape.param``.

```{pyodide}
shapes = [NGon(), Circle()]

class ShapeViewer(param.Parameterized):

    shape = param.ObjectSelector(default=shapes[0], objects=shapes)

    @param.depends('shape')
    def view(self):
        return self.shape.view()

    @param.depends('shape', 'shape.radius')
    def title(self):
        return '## %s (radius=%.1f)' % (type(self.shape).__name__, self.shape.radius)

    def panel(self):
        return pn.Column(self.title, self.view)
```

Now that we have a class with subobjects we can display it as usual.  Three main options control how the subobject is rendered:

* ``expand``: Whether the subobject is expanded on initialization (``default=False``).
* ``expand_button``: Whether there should be a button to toggle expansion; otherwise it is fixed to the initial ``expand`` value (``default=True``).
* ``expand_layout``: A layout type or instance to expand the plot into (``default=Column``).

Let us start with the default view, which provides a toggle button to expand the subobject as desired:


```{pyodide}
viewer = ShapeViewer()

pn.Row(viewer.param, viewer.panel())
```

Alternatively we can provide a completely separate ``expand_layout`` instance to the Param pane and request that it always remains expanded using the ``expand`` and ``expand_button`` option. This allows us to lay out the main widgets and the subobject's widgets separately:


```{pyodide}
viewer = ShapeViewer()

expand_layout = pn.Column()

pn.Row(
    pn.Column(
        pn.panel(viewer.param, expand_button=False, expand=True, expand_layout=expand_layout),
        "#### Subobject parameters:",
        expand_layout),
    viewer.panel())
```

---

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index.md) for context on this and other Panel APIs
