# Declarative API

The [Param](http://param.holoviz.org) library allows expressing the parameters of a class (or a hierarchy of classes) completely independently of a GUI implementation. Panel and other libraries can then take those parameter declarations and turn them into a GUI to control the parameters. This approach allows the parameters controlling some computation to be captured specifically and explicitly (but as abstract parameters, not as widgets). Then thanks to the `@param.depends` decorator (similar to `@panel.depends` but for use in Parameterized classes without any dependency on Panel), it is then possible to directly express the dependencies between the parameters and the computation defined in some method on the class, all without ever importing Panel or any other GUI library. The resulting objects can then be used in both GUI and non-GUI contexts (batch computations, scripts, servers).

The parameterized approach is a powerful way to encapsulate computation in self-contained classes, taking advantage of object-oriented programming patterns. It also makes it possible to express a problem completely independently from Panel or any other GUI code, while still getting a GUI for free as a last step. For more detail on using this approach see the [how-to guides on declarative UIs with Param](../../how_to/param/index.md).

## Pros:

+ Declarative way of expressing parameters and dependencies between parameters and computation
+ Information about parameter types and allowed ranges is stored directly with the code that uses it, making it easier for programmers to reason about the core code and to detect issues with user-provided values.
+ Like the reactive API, the resulting core code is not tied to any particular GUI framework and can be used in other contexts as well
+ Compared to the reactive API, the core code itself can _also_ be updated and improved without necessarily needing any changes to the GUI code, because the GUI code rarely needs to encode detailed information about the core code.

## Cons:

- Requires writing Python classes, which are not otherwise commonly used in data science
- Less explicit about widgets to use for each parameter; can be harder to customize behavior than if widgets are instantiated explicitly

## Explanation

In this model we declare a subclass of ``param.Parameterized``, declare the parameters we want at the class level, make an instance of the class, and finally lay out the parameters and plot method of the class.

## Example

```{pyodide}
import hvplot.pandas
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

import panel as pn
pn.Row(explorer.param, explorer.plot)
```

Note how only the very last two lines involve Panel at all, and that they do not include any information about the underlying Parameters or their types. That way the GUI code can be maintained fully independently from the rest of the code, without complex linkages like encoding the list of columns at both the code level and the GUI level. In a small app like this the benefit is minimal, but in a large, complex codebase, being able to build a GUI that is not tightly tied to the underlying code makes it much easier to focus on what the code _does_ separately from how the GUI looks.
