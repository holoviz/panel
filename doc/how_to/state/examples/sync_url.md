# Sync Widgets and URL

```{pyodide}
import panel as pn

pn.extension(design='material', template='material')

pn.state.template.main_max_width = '768px'
```

This example demonstrates how to sync widget state with the URL bar, restoring it from the URL parameters on page load and updating it when the widgets change.

```{pyodide}
widget = pn.widgets.FloatSlider(name='Slider', start=0, end=10)
widget2 = pn.widgets.TextInput(name='Text')
widget3 = pn.widgets.RangeSlider(name='RangeSlider', start=0, end=10)

if pn.state.location:
    pn.state.location.sync(widget, {'value': 'slider_value'})
    pn.state.location.sync(widget2, {'value': 'text_value'})
    pn.state.location.sync(widget3, {'value': 'range_value'})

pn.Column(widget, widget2, widget3).servable()
```
