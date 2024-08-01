# Plotly Link

```{pyodide}
import numpy as np
import panel as pn

pn.extension('plotly', template='bootstrap')
```

Since Plotly plots are represented as simple JavaScript objects, we can easily define a JS callback to modify the data and trigger an update in a plot:

```{pyodide}
xs, ys = np.mgrid[-3:3:0.2, -3:3:0.2]
contour = dict(ncontours=4, type='contour', z=np.sin(xs**2*ys**2))
layout = {'width': 600, 'height': 500, 'margin': {'l': 8, 'b': 8, 'r': 8, 't': 8}}
fig = dict(data=contour, layout=layout)
plotly_pane = pn.pane.Plotly(fig, width=600, height=500)

buttons = pn.widgets.RadioButtonGroup(value='Medium', options=['Low', 'Medium', 'High'], button_type="success")

range_callback = """
var ncontours = [2, 5, 10]
target.data[0].ncontours = ncontours[source.active]
target.properties.data.change.emit()
"""

buttons.jslink(plotly_pane, code={'active': range_callback})

pn.Column(buttons, plotly_pane).servable()
```
