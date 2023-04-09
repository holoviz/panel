# Bokeh property editor

```{pyodide}
import numpy as np
import panel as pn

pn.extension(template='bootstrap')
```

Bokeh's property system defines the valid properties for all the different Bokeh models. Using ``jslink`` we can easily tie a widget value to Bokeh properties on another widget or plot. This example defines functions that generate a property editor for the most common Bokeh properties. First, we define two functions that generate a set of widgets linked to a plot:

```{pyodide}
from bokeh.core.enums import LineDash, LineCap, MarkerType, NamedColor
from bokeh.core.property.vectorization import Value
from bokeh.models.plots import Model, _list_attr_splat

def meta_widgets(model, width=500):
    tabs = pn.Tabs(width=width)
    widgets = get_widgets(model, width=width-25)
    if widgets:
        tabs.append((type(model).__name__, widgets))
    for p, v in model.properties_with_values().items():
        if isinstance(v, _list_attr_splat):
            v = v[0]
        if isinstance(v, Model):
            subtabs = meta_widgets(v)
            if subtabs is not None:
                tabs.append((p.title(), subtabs))

    if hasattr(model, 'renderers'):
        for r in model.renderers:
            tabs.append((type(r).__name__, meta_widgets(r)))
    if hasattr(model, 'axis') and isinstance(model.axis, list):
        for pre, axis in zip('XY', model.axis):
            tabs.append(('%s-Axis' % pre, meta_widgets(axis)))
    if hasattr(model, 'grid'):
        for pre, grid in zip('XY', model.grid):
            tabs.append(('%s-Grid' % pre, meta_widgets(grid)))
    if not widgets and not len(tabs) > 1:
        return None
    elif not len(tabs) > 1:
        return tabs[0]
    return tabs

def get_widgets(model, skip_none=True, **kwargs):
    widgets = []
    for p, v in model.properties_with_values().items():
        if isinstance(v, Value):
            v = v.value
        if v is None and skip_none:
            continue

        ps = dict(name=p, value=v, **kwargs)
        if 'alpha' in p:
            w = pn.widgets.FloatSlider(start=0, end=1, **ps)
        elif 'color' in p:
            if v in list(NamedColor):
                w = pn.widgets.Select(options=list(NamedColor), **ps)
            else:
                w = pn.widgets.ColorPicker(**ps)
        elif p=="width":
            w = pn.widgets.IntSlider(start=400, end=800, **ps)
        elif p in ["inner_width", "outer_width"]:
            w = pn.widgets.IntSlider(start=0, end=20, **ps)
        elif p.endswith('width'):
            w = pn.widgets.FloatSlider(start=0, end=20, **ps)
        elif 'marker' in p:
            w = pn.widgets.Select(options=list(MarkerType), **ps)
        elif p.endswith('cap'):
            w = pn.widgets.Select(options=list(LineCap), **ps)
        elif p == 'size':
            w = pn.widgets.FloatSlider(start=0, end=20, **ps)
        elif p.endswith('text') or p.endswith('label'):
            w = pn.widgets.TextInput(**ps)
        elif p.endswith('dash'):
            patterns = list(LineDash)
            w = pn.widgets.Select(options=patterns, value=v or patterns[0], **kwargs)
        else:
            continue
        w.jslink(model, value=p)
        widgets.append(w)
    return pn.Column(*sorted(widgets, key=lambda w: w.name))

# Having defined these helper functions we can now declare a plot and use the ``meta_widgets`` function to generate the GUI:

from bokeh.plotting import figure

p = figure(title='This is a title', x_axis_label='x-axis', y_axis_label='y-axis')
xs = np.linspace(0, 10)
r = p.scatter(xs, np.sin(xs))

editor=pn.Row(meta_widgets(p), p)

editor.servable()
```
