# Create Indicators With ReactiveHTML

## Basic Progress Indicator

Here we create a basic progress indicator

```{pyodide}
import param
import panel as pn
from panel.reactive import ReactiveHTML

pn.extension()

class CustomProgress(ReactiveHTML):
  value = param.Integer(0, bounds=(0,100))
  color = param.Color("#007bff")

  _template=  """
<div id="progress-bar" style="background-color: ${color}; height: 100%; width: ${value}%;"></div>
"""

progress = CustomProgress(
  value=55, styles={"border": "2px solid lightgray"}, height=100, sizing_mode="stretch_width"
)
pn.Column(progress, progress.param.value, progress.param.color)
```
