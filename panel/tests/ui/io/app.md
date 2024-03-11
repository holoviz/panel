```{pyodide}
import panel as pn

pn.pane.Markdown(f"{pn.state.cache['num']}", css_classes=['counter']).servable()
```
