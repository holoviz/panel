# Reactive Tables

```{pyodide}
import param
import panel as pn

from bokeh.sampledata.iris import flowers
from bokeh.sampledata.autompg import autompg_clean
from bokeh.sampledata.population import data
from panel.viewable import Viewer

pn.extension(template='fast')
```

This example demonstrates Panel's reactive programming paradigm using the Param library to express parameters, plus methods with computation depending on those parameters. This pattern can be used to update the displayed views whenever a parameter value changes, without re-running computation unnecessarily.

```{pyodide}
class ReactiveTables(Viewer):

    dataset = param.ObjectSelector(default='iris', objects=['iris', 'autompg', 'population'])

    rows = param.Integer(default=10, bounds=(0, 19))

    @param.depends('dataset')
    def data(self):
        if self.dataset == 'iris':
            return flowers
        elif self.dataset == 'autompg':
            return autompg_clean
        else:
            return data

    @param.depends('data')
    def summary(self):
        return self.data().describe()

    @param.depends('data', 'rows')
    def table(self):
        return self.data().iloc[:self.rows]

    def __panel__(self):
        return pn.Row(
            pn.Param(self, name="Settings", width=300),
			pn.Spacer(width=10),
            pn.Column(
			    "## Description",
				pn.pane.DataFrame(self.summary, sizing_mode='stretch_width'),
				"## Table",
				pn.pane.DataFrame(self.table, sizing_mode='stretch_width'),
			)
        )

ReactiveTables().servable()
```
