# Declare parameter dependencies

This guide addresses how to leverage `@param.depends` to express dependencies and trigger events based on UI interactions.

```{admonition} Prerequisites
1. The [How to > Generate Widgets from Parameters](./uis) guide demonstrates the automatic generation of widgets without dependencies.
```

---

Declaring parameters is usually only the beginning of a workflow. In most applications these parameters are then tied to some computation. To express the relationship between a computation and the parameters it depends on, the ``param.depends`` decorator may be used on Parameterized methods. This decorator provides a hint to Panel and other Param-based libraries (e.g. HoloViews) that the method should be re-evaluated when a parameter changes.

As a straightforward example without any additional dependencies we will write a small class that returns an ASCII representation of a sine wave, which depends on `phase` and `frequency` parameters. If we supply the ``.view`` method to a panel, it will automatically recompute and update the view when one or more of the parameters changes:

```{pyodide}
import panel as pn
import param
import numpy as np

pn.extension()

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

The parameterized and annotated ``view`` method could return any one of the types handled by the [Pane objects](../../explanation/components/components_overview.md#panes) Panel provides, making it easy to link parameters and their associated widgets to a plot or other output. Parameterized classes can therefore be a very useful pattern for encapsulating a part of a computational workflow with an associated visualization, declaratively expressing the dependencies between the parameters and the computation.

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

---

## Related Resources

- See the [Explanation > APIs](../../explanation/api/index) for context on this and other Panel APIs
