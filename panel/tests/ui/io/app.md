```{pyodide}
import panel as pn

if 'num' in pn.state.cache:
    pn.state.cache['num'] += 1
else:
    pn.state.cache['num'] = 0

pn.pane.Markdown(f"{pn.state.cache['num']}", css_classes=['counter']).servable()
```
