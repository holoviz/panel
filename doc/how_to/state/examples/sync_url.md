# Sync Widgets and URL

```{pyodide}
import panel as pn

pn.extension(design='material', template='material')

pn.state.template.main_max_width = '768px'
```

This example demonstrates how to sync widget state with the URL bar, restoring it from the URL parameters on page load and updating it when the widgets change.

```{pyodide}
widget = pn.ui.FloatSlider(label='Slider', start=0, end=10)
widget2 = pn.ui.TextInput(label='Text')
widget3 = pn.ui.RangeSlider(label='RangeSlider', start=0, end=10)

if pn.state.location:
    pn.state.location.sync(widget, {'value': 'slider_value'})
    pn.state.location.sync(widget2, {'value': 'text_value'})
    pn.state.location.sync(widget3, {'value': 'range_value'})

pn.ui.Column(widget, widget2, widget3).servable()
```
