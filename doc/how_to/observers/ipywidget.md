# Observe ipywidgets

In this how-to guide we show how-to easily enable interaction with ipywidgets via familiar APIs from Param like watch, bind, depends, and rx.

## Overview

The `pn.observers.ipywidget` module provides functions to synchronize the traits of an ipywidget with a Parameterized object, a Panel widget, or an `rx` value. It also provides a `ModelViewer` class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

### Terminology

- **Traitlets**: A library for creating classes (`HasTraits`) with observable attributes (called *traits*).
- **Param**: A library similar to Traitlets, for creating classes (`Parameterized`) with watchable attributes (called *parameters*).
- **ipywidgets**: Builds on Traitlets to create interactive widgets for Jupyter notebooks.
- **widget**: Refers to ipywidgets unless otherwise stated.
- **model**: Refers to Traitlets classes including ipywidgets.
- **names**: Refers to the names of the traits/ parameters to synchronize. Can be an iterable or dictionary mapping from trait names to parameter names.

### Classes

- **`ModelParameterized`**: An abstract Parameterized base class for wrapping a traitlets HasTraits class or instance.
- **`ModelViewer`**: An abstract base class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

### Functions

- **`create_rx`**: Creates `rx` values from traits of a model, each synced to a trait of the model.
- **`sync_with_parameterized`**: Syncs the traits of a model with the parameters of a Parameterized object.
- **`sync_with_widget`**: Syncs the named trait of the model with the value of a Panel widget.
- **`sync_with_rx`**: Syncs a single trait of a model with an `rx` value.

All synchronization is bidirectional. We only synchronize the top-level traits/ parameters and not the nested ones.

### Synchronize the trait of an ipywidget with a Panel widget

Use `sync_with_widget` to synchronize a trait of an ipywidget with a Panel widget.

```pyodide
import panel as pn
import ipyleaflet as ipyl

pn.extension("ipywidgets")

leaflet_map = ipyl.Map()

zoom_widget = pn.widgets.FloatSlider(value=2.0, start=1.0, end=24.0, name="Zoom")
zoom_control_widget = pn.widgets.Checkbox(name="Show Zoom Control")

pn.observers.ipywidget.sync_with_widget(leaflet_map, zoom_widget, name="zoom")
pn.observers.ipywidget.sync_with_widget(leaflet_map, zoom_control_widget, name="zoom_control")
pn.Column(leaflet_map, zoom_widget, zoom_control_widget).servable()
```

## Synchronize an ipywidget with a Parameterized object

Use `sync_with_parameterized` to synchronize a widget with a Parameterized object.

```pyodide
import panel as pn
import ipyleaflet as ipyl
import param

pn.extension("ipywidgets")

leaflet_map = ipyl.Map()

class Map(param.Parameterized):
    center = param.List(default=[52.204793, 360.121558])
    zoom = param.Number(default=4, bounds=(0, 24), step=1)

parameterized = Map()

pn.observers.ipywidget.sync_with_parameterized(
    model=leaflet_map, parameterized=parameterized
)
pn.Column(leaflet_map, parameterized.param.zoom, parameterized.param.center).servable()
```

The `sync_with_parameterized` function synchronizes the shared traits/ parameters `center` and `zoom` between the `leaflet_map` and `parameterized` objects.

Use the `names` arguments to specify a subset of traits/ parameters to synchronize:

```python
pn.observers.ipywidget.sync_with_parameterized(
    model=leaflet_map, parameterized=parameterized, names=("center",)
)
```

The `names` argument may also be a `dict` mapping from trait names to parameter names:

```pyodide
import panel as pn
import ipyleaflet as ipyl
import param

pn.extension("ipywidgets")

leaflet_map = ipyl.Map()

class Map(param.Parameterized):
    zoom_level = param.Number(default=4, bounds=(0, 24), step=1)

parameterized = Map()

pn.observers.ipywidget.sync_with_parameterized(
    model=leaflet_map, parameterized=parameterized, names={"zoom": "zoom_level"}
)
pn.Column(leaflet_map, parameterized.param.zoom_level).servable()
```

### Create a Viewer from an ipywidget instance

To create a `Viewer` object from a widget instance, use the `ModelViewer` class:

```pyodide
import panel as pn
import ipyleaflet as ipyl
import param

pn.extension("ipywidgets")

leaflet_map = ipyl.Map()

viewer = pn.observers.ipywidget.ModelViewer(model=leaflet_map)
pn.Column(viewer, viewer.controls()).servable()
```

Use the `names` arguments to specify a subset of traits/ parameters to synchronize:

```python
pn.observers.ipywidget.sync_with_parameterized(
    model=leaflet_map, parameterized=parameterized, names=("center",)
)
```

The `names` argument may also be a `dict` mapping from trait names to parameter names.

### Create a Viewer from an ipywidget class

To create a `Viewer` class from a widget class, use the `ModelViewer` class:

```pyodide
import panel as pn
import ipyleaflet as ipyl
import param

pn.extension("ipywidgets")


class MapViewer(pn.observers.ipywidget.ModelViewer):
    _model_class = ipyl.Map
    _names = ["center", "zoom"]

    zoom = param.Number(4, bounds=(0, 24), step=1)


viewer = MapViewer(sizing_mode="stretch_both")

pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
```

The `_names` is an optional iterable or dict. Its used to specify which traits to synchronize to which parameters to synchronize.

### Create a reactive value from the trait of an ipywidget

Use `create_rx` to create a reactive value from the trait of an ipywidget.

```pyodide
import panel as pn
import ipyleaflet as ipyl

pn.extension("ipywidgets")

leaflet_map = ipyl.Map(zoom=4)
zoom, zoom_control = pn.observers.ipywidget.create_rx(
    leaflet_map, "zoom", "zoom_control"
)

pn.Column(
    leaflet_map,
    zoom.rx.pipe(
        lambda x: f"**Value**: {x}, **Zoom Control**: " + zoom_control.rx.pipe(str)
    ),
).servable()
```

## References

- [IPyWidget Pane Reference](../../reference/panes/IPyWidget.ipynb)
