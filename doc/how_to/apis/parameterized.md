# Parameterized Classes

The [Param](http://param.holoviz.org) library allows expressing the parameters of a class (or a hierarchy of classes) completely independently of a GUI implementation. Panel and other libraries can then take those parameter declarations and turn them into a GUI to control the parameters. This approach allows the parameters controlling some computation to be captured specifically and explicitly (but as abstract parameters, not as widgets). Then thanks to the `@param.depends` decorator (similar to `@panel.depends` but for use in Parameterized classes without any dependency on Panel), it is then possible to directly express the dependencies between the parameters and the computation defined in some method on the class, all without ever importing Panel or any other GUI library. The resulting objects can then be used in both GUI and non-GUI contexts (batch computations, scripts, servers).

The parameterized approach is a powerful way to encapsulate computation in self-contained classes, taking advantage of object-oriented programming patterns. It also makes it possible to express a problem completely independently from Panel or any other GUI code, while still getting a GUI for free as a last step. For more detail on using this approach see the [Param user guide](../user_guide/Param).

## Pros:

+ Declarative way of expressing parameters and dependencies between parameters and computation
+ The resulting code is not tied to any particular GUI framework and can be used in other contexts as well

## Cons:

- Requires writing classes
- Less explicit about widgets to use for each parameter; can be harder to customize behavior than if widgets are instantiated explicitly

## Explanation

In this model we declare a subclass of ``param.Parameterized``, declare the parameters we want at the class level, make an instance of the class, and finally lay out the parameters and plot method of the class.

## Example

```{pyodide}
import hvplot.pandas
import panel as pn
import param

from bokeh.sampledata.autompg import autompg

columns = list(autompg.columns[:-2])

class MPGExplorer(param.Parameterized):

    x = param.Selector(objects=columns)
    y = param.Selector(default='hp', objects=columns)
    color = param.Color(default='#0f0f0f')

    @param.depends('x', 'y', 'color') # optional in this case
    def plot(self):
        return autompg.hvplot.scatter(self.x, self.y, c=self.color, padding=0.1)

explorer = MPGExplorer()

pn.Row(explorer.param, explorer.plot)
```
