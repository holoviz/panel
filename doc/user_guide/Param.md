# Using Param with Panel

Panel supports using parameters and dependencies between parameters as expressed by ``param`` in a simple way to encapsulate dashboards as declarative, self-contained classes.

Parameters are Python attributes extended using the [Param library](https://github.com/holoviz/param) to support types, ranges, and documentation, which turns out to be just the information you need to automatically create widgets for each parameter.

Additionally Panel provides support for linking parameters to the URL query string to allow parameterizing an app very easily.

## Parameters and widgets

To use this approach, first declare some Parameterized classes with various Parameters:


```{pyodide}
import param
import pandas as pd
import datetime as dt

class BaseClass(param.Parameterized):
    x                       = param.Parameter(default=3.14, doc="X position")
    y                       = param.Parameter(default="Not editable", constant=True)
    string_value            = param.String(default="str", doc="A string")
    num_int                 = param.Integer(50000, bounds=(-200, 100000))
    unbounded_int           = param.Integer(23)
    float_with_hard_bounds  = param.Number(8.2, bounds=(7.5, 10))
    float_with_soft_bounds  = param.Number(0.5, bounds=(0, None), softbounds=(0,2))
    unbounded_float         = param.Number(30.01, precedence=0)
    hidden_parameter        = param.Number(2.718, precedence=-1)
    integer_range           = param.Range(default=(3, 7), bounds=(0, 10))
    float_range             = param.Range(default=(0, 1.57), bounds=(0, 3.145))
    dictionary              = param.Dict(default={"a": 2, "b": 9})


class Example(BaseClass):
    """An example Parameterized class"""
    timestamps = []

    boolean                 = param.Boolean(True, doc="A sample Boolean parameter")
    color                   = param.Color(default='#FFFFFF')
    date                    = param.Date(dt.datetime(2017, 1, 1),
                                         bounds=(dt.datetime(2017, 1, 1), dt.datetime(2017, 2, 1)))
    dataframe               = param.DataFrame(pd._testing.makeDataFrame().iloc[:3])
    select_string           = param.ObjectSelector(default="yellow", objects=["red", "yellow", "green"])
    select_fn               = param.ObjectSelector(default=list,objects=[list, set, dict])
    int_list                = param.ListSelector(default=[3, 5], objects=[1, 3, 5, 7, 9], precedence=0.5)
    single_file             = param.FileSelector(path='../../*/*.py*', precedence=0.5)
    multiple_files          = param.MultiFileSelector(path='../../*/*.py?', precedence=0.5)
    record_timestamp        = param.Action(lambda x: x.timestamps.append(dt.datetime.utcnow()),
                                           doc="""Record timestamp.""", precedence=0.7)

Example.num_int
```

As you can see, declaring Parameters depends only on the separate Param library.  Parameters are a simple idea with some properties that are crucial for helping you create clean, usable code:

- The Param library is pure Python with no dependencies, which makes it easy to include in any code without tying it to a particular GUI or widgets library, or even to the Jupyter notebook.
- Parameter declarations focus on semantic information relevant to your domain, allowing you to avoid polluting your domain-specific code with anything that ties it to a particular way of displaying or interacting with it.
- Parameters can be defined wherever they make sense in your inheritance hierarchy, allowing you to document, type, and range-limit them _once_, with all of those properties inherited by any base class.  E.g. parameters work the same here whether they were declared in `BaseClass` or `Example`, which makes it easy to provide this metadata once, and avoiding duplicating it throughout the code wherever ranges or types need checking or documentation needs to be stored.

If you then decide to use these Parameterized classes in a notebook or web-server environment, you can `import panel` and easily display and edit the parameter values as an optional additional step:


```{pyodide}
import panel as pn

pn.extension()

base = BaseClass()
pn.Row(Example.param, base.param)
```

As you can see, Panel does not need to be provided with any knowledge of your domain-specific application, not even the names of your parameters; it simply displays widgets for whatever Parameters may have been defined on that object.  Using Param with Panel thus achieves a nearly complete separation between your domain-specific code and your display code, making it vastly easier to maintain both of them over time.  Here even the `msg` button behavior was specified declaratively, as an action that can be invoked (printing "Hello") independently of whether it is used in a GUI or other context.

Interacting with the widgets above is only supported in the notebook and on Bokeh server, but you can also export static renderings of the widgets to a file or web page.

By default, editing values in this way requires you to run the notebook cell by cell -- when you get to the above cell, edit the values as you like, and then move on to execute subsequent cells, where any reference to those parameter values will use your interactively selected setting:


```{pyodide}
Example.unbounded_int
```


```{pyodide}
Example.num_int
```

The reverse is possible; editing a parameter from Python will automatically update any widgets that were generated from the parameter:


```{pyodide}
Example.int_list = [1, 7]
```

Example.timestamps records the times you pressed the "record timestamp" button.


```{pyodide}
Example.timestamps
```

Passing the ``.param`` object renders the full set of widgets, while passing a single parameter will display just one widget. In this way we can easily declare exactly which parameters to display:


```{pyodide}
pn.Row(Example.param.float_range, Example.param.num_int)
```

As you can see, you can access the parameter values at the class level from within the notebook to control behavior explicitly, e.g. to select what to show in subsequent cells.  Moreover, any instances of the Parameterized classes in your own code will now use the new parameter values unless specifically overridden in that instance, so you can now import and use your domain-specific library however you like, knowing that it will use your interactive selections wherever those classes appear.  None of the domain-specific code needs to know or care that you used Panel; it will simply see new values for whatever attributes were changed interactively.  Panel thus allows you to provide notebook-specific, domain-specific interactive functionality without ever tying your domain-specific code to the notebook environment. This default behavior can also be modified if you wish, as outlined below.

### Custom widgets

In the previous section we saw how parameters can automatically be turned into widgets. This is possible because internally Panel maintains a mapping between parameter types and widget types. However, sometimes the default widget does not provide the most convenient UI and we want to provide an explicit hint to Panel to tell it how to render a parameter. This is possible using the ``widgets`` argument to the `Param` pane. Using the ``widgets`` keyword we can declare a mapping between the parameter name and the type of widget that is desired (as long as the widget type supports the types of values held by the parameter type).

As an example, we can map a string and a number Selector to a RadioButtonGroup and DiscretePlayer respectively.


```{pyodide}
class CustomExample(param.Parameterized):
    """An example Parameterized class"""

    select_string = param.Selector(objects=["red", "yellow", "green"])
    autocomplete_string = param.Selector(default='', objects=["red", "yellow", "green"], check_on_set=False)
    select_number = param.Selector(objects=[0, 1, 10, 100])


pn.Param(CustomExample.param, widgets={
    'select_string': pn.widgets.RadioButtonGroup,
    'autocomplete_string': pn.widgets.AutocompleteInput,
    'select_number': pn.widgets.DiscretePlayer}
)
```

Also, it's possible to pass arguments to the widget in order to customize it. Instead of passing the widget, pass a dictionary with the desired options. Use the ``widget_type`` keyword to map the widget.

Taking up the previous example.


```{pyodide}
pn.Param(CustomExample.param, widgets={
    'select_string': {'widget_type': pn.widgets.RadioButtonGroup, 'button_type': 'success'},
    'autocomplete_string': {'widget_type': pn.widgets.AutocompleteInput, 'placeholder': 'Find a color...'},
    'select_number': pn.widgets.DiscretePlayer}
)
```

However it is also possible to explicitly construct a widget from a parameter using the `.from_param` method, which makes it easy to override widget settings using keyword arguments:


```{pyodide}
pn.widgets.IntSlider.from_param(Example.param.unbounded_int, start=0, end=100)
```

### Custom name

By default, a param Pane has a title that is derived from the class name of its `Parameterized` object. Using the ``name`` keyword we can set any title to the pane, e.g. to improve the user interface.


```{pyodide}
pn.Param(CustomExample.param, name="Custom Name")
```

### Sort

You can sort the widgets alphabetically by setting `sort=True`


```{pyodide}
pn.Param(CustomExample.param, sort=True, name="Sort by Label Example")
```

You can also specify a custom sort function that takes the (parameter name, Parameter instance) as input.


```{pyodide}
def sort_func(x):
    return len(x[1].label)
pn.Param(CustomExample.param, sort=sort_func, name="Sort by Label Length Example")
```

## Parameter dependencies

Declaring parameters is usually only the beginning of a workflow. In most applications these parameters are then tied to some computation. To express the relationship between a computation and the parameters it depends on, the ``param.depends`` decorator may be used on Parameterized methods. This decorator provides a hint to Panel and other Param-based libraries (e.g. HoloViews) that the method should be re-evaluated when a parameter changes.

As a straightforward example without any additional dependencies we will write a small class that returns an ASCII representation of a sine wave, which depends on `phase` and `frequency` parameters. If we supply the ``.view`` method to a panel, it will automatically recompute and update the view when one or more of the parameters changes:


```{pyodide}
import numpy as np


class Sine(param.Parameterized):

    phase = param.Number(default=0, bounds=(0, np.pi))

    frequency = param.Number(default=1, bounds=(0.1, 2))

    @param.depends('phase', 'frequency')
    def view(self):
        y = np.sin(np.linspace(0, np.pi * 3, 40) * self.frequency + self.phase)
        y = ((y - y.min()) / y.ptp()) * 20
        array = np.array(
            [list((' ' * (int(round(d)) - 1) + '*').ljust(20)) for d in y])
        return pn.pane.Str('\n'.join([''.join(r) for r in array.T]), height=380, width=500)


sine = Sine(name='ASCII Sine Wave')
pn.Row(sine.param, sine.view)
```

The parameterized and annotated ``view`` method could return any one of the types handled by the [Pane objects](./Components.md#Panes) Panel provides, making it easy to link parameters and their associated widgets to a plot or other output. Parameterized classes can therefore be a very useful pattern for encapsulating a part of a computational workflow with an associated visualization, declaratively expressing the dependencies between the parameters and the computation.

By default, a Param pane will show widgets for all parameters with a `precedence` value above the value `pn.Param.display_threshold`, so you can use `precedence` to automatically hide parameters that are not meant to have widgets.  You can also explicitly choose which parameters should have widgets in a given pane, by passing a `parameters` argument.  For example, this code gives a `phase` widget, while maintaining `sine.frequency` at the initial value of `1`:


```{pyodide}
pn.Row(pn.panel(sine.param, parameters=['phase']), sine.view)
```

Another common pattern is linking the values of one parameter to another parameter, e.g. when dependencies between parameters exist. In the example below we will define two parameters, one for the continent and one for the country. Since we want the selection of valid countries to change when we change the continent, we define a method to do that for us. In order to link the two we express the dependency using the ``param.depends`` decorator and then ensure that we will run the method whenever the continent changes by setting ``watch=True``.

We also define a ``view`` method that returns an HTML iframe displaying the country using Google Maps.


```{pyodide}
class GoogleMapViewer(param.Parameterized):

    continent = param.ObjectSelector(default='Asia', objects=['Africa', 'Asia', 'Europe'])

    country = param.ObjectSelector(default='China', objects=['China', 'Thailand', 'Japan'])

    _countries = {'Africa': ['Ghana', 'Togo', 'South Africa', 'Tanzania'],
                  'Asia'  : ['China', 'Thailand', 'Japan'],
                  'Europe': ['Austria', 'Bulgaria', 'Greece', 'Portugal', 'Switzerland']}

    @param.depends('continent', watch=True)
    def _update_countries(self):
        countries = self._countries[self.continent]
        self.param['country'].objects = countries
        self.country = countries[0]

    @param.depends('country')
    def view(self):
        iframe = """
        <iframe width="800" height="400" src="https://maps.google.com/maps?q={country}&z=6&output=embed"
        frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe>
        """.format(country=self.country)
        return pn.pane.HTML(iframe, height=400)

viewer = GoogleMapViewer(name='Google Map Viewer')
pn.Row(viewer.param, viewer.view)
```

Whenever the continent changes Param will now eagerly execute the ``_update_countries`` method to change the list of countries that is displayed, which in turn triggers an update in the view method updating the map. Note that there is no need to add ``watch=True`` to decorators of methods that are passed to a Panel layout (e.g. ``viewer.View`` being passed to ``pn.Row`` here), because Panel will already handle dependencies on those methods, executing the method automatically when the dependent parameters change. Indeed, if you specify ``watch=True`` for such a method, the method will get invoked _twice_ each time a dependency changes (once by Param internally and once by Panel), so you should reserve ``watch=True`` only for methods that aren't otherwise being monitored for dependencies.

### Parameter subobjects

``Parameterized`` objects often have parameter values which are themselves ``Parameterized`` objects, forming a tree-like structure. Panel allows you to edit not just the main object's parameters but also lets you drill down to the subobject. Let us first define some classes declaring a hierarchy of Shape classes which draw a Bokeh plot of the selected shape:


```{pyodide}
from bokeh.plotting import figure


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

In this user guide we have seen how to leverage Param to declare parameters, which Panel can then turn into a GUI with little additionl effort or code. We have also seen how to link parameters to views and to other parameters using the ``param.depends`` operator. This approach allows building complex and reactive panels. In the [pipelines user guide](Pipelines.md) we can discover how to link multiple such classes into pipelines, making it possible to encapsulate complex workflows in clean self-contained classes.
