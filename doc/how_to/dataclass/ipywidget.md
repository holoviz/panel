# Interact with ipywidgets

This how-to guide demonstrates how to easily enable interaction with [ipywidgets](https://ipywidgets.readthedocs.io/en/stable/) using familiar APIs from Panel and [Param](https://param.holoviz.org/), such as `watch`, `bind`, `depends`, and `rx`.

## Overview

The `pn.dataclass` module provides functions to synchronize the *traits* of an ipywidget with a Parameterized object, a Panel widget, or an `rx` value. It also provides a `ModelViewer` class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

### Terminology

- **Traitlets**: A library for creating dataclass like models (`HasTraits`) with observable fields (called *traits*).
- **ipywidgets**: A library for creating interactive widgets for notebooks. Its base class `Widget` derives from `HasTraits`.
- **widget**: Refers to ipywidgets `Widget` classes or instances unless otherwise stated.
- **model**: Refers to Traitlets `HasTraits` and ipywidgets `Widget` classes or instances.
- **names**: Refers to the names of the traits/parameters to synchronize. Can be an iterable or a dictionary mapping from trait names to parameter names.

### Classes

- **`ModelParameterized`**: An abstract Parameterized base class for wrapping a Traitlets `HasTraits` class or instance.
- **`ModelViewer`**: An abstract base class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

### Functions

- **`to_rx`**: Creates `rx` values from traits of a model, each synced to a trait of the model.
- **`sync_with_parameterized`**: Syncs the traits of a model with the parameters of a Parameterized object.
- **`sync_with_widget`**: Syncs a trait of the model with the value of a Panel widget.
- **`sync_with_rx`**: Syncs a single trait of a model with an `rx` value.

All synchronization is bidirectional. Only top-level traits/parameters are synchronized, not nested ones.

## Synchronize Traits of an ipywidget with Panel Widgets

Use `sync_with_widget` to synchronize a trait of an ipywidget with the `value` parameter of a Panel widget.

```{pyodide}
import panel as pn
import ipyleaflet as ipyl

pn.extension("ipywidgets")

leaflet_map = ipyl.Map()

zoom_widget = pn.widgets.FloatSlider(value=4.0, start=1.0, end=24.0, name="Zoom")
zoom_control_widget = pn.widgets.Checkbox(name="Show Zoom Control")

pn.dataclass.sync_with_widget(leaflet_map, zoom_widget, name="zoom")
pn.dataclass.sync_with_widget(leaflet_map, zoom_control_widget, name="zoom_control")
pn.Column(leaflet_map, zoom_widget, zoom_control_widget).servable()
```

## Synchronize an ipywidget with a Parameterized Object

Use `sync_with_parameterized` to synchronize an ipywidget with a Parameterized object.

```{pyodide}
import panel as pn
import ipyleaflet as ipyl
import param

pn.extension("ipywidgets")

leaflet_map = ipyl.Map()

class Map(param.Parameterized):
    center = param.List(default=[52.204793, 360.121558])
    zoom = param.Number(default=4, bounds=(0, 24), step=1)

parameterized = Map()

pn.dataclass.sync_with_parameterized(
    model=leaflet_map, parameterized=parameterized
)
pn.Column(leaflet_map, parameterized.param.zoom, parameterized.param.center).servable()
```

The `sync_with_parameterized` function synchronizes the shared traits/parameters `center` and `zoom` between the `leaflet_map` and `parameterized` objects.

To specify a subset of traits/parameters to synchronize, use the `names` argument:

```python
pn.dataclass.sync_with_parameterized(
    model=leaflet_map, parameterized=parameterized, names=("center",)
)
```

The `names` argument can also be a dictionary mapping trait names to parameter names:

```{pyodide}
import panel as pn
import ipyleaflet as ipyl
import param

pn.extension("ipywidgets")

leaflet_map = ipyl.Map()

class Map(param.Parameterized):
    zoom_level = param.Number(default=4, bounds=(0, 24), step=1)

parameterized = Map()

pn.dataclass.sync_with_parameterized(
    model=leaflet_map, parameterized=parameterized, names={"zoom": "zoom_level"}
)
pn.Column(leaflet_map, parameterized.param.zoom_level).servable()
```

## Create a Viewer from an ipywidget Instance

To create a `Viewer` object from a ipywidget instance, use the `ModelViewer` class:

```{pyodide}
import panel as pn
import ipyleaflet as ipyl

pn.extension("ipywidgets")

leaflet_map = ipyl.Map(zoom=4)

viewer = pn.dataclass.ModelViewer(model=leaflet_map, sizing_mode="stretch_both")
pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
```

Check out the parameters to the left of the map, there you will find all the traits of the `leaflet_map` instance. Try changing some.

To specify a subset of traits/parameters to synchronize, use the `names` argument:

```python
viewer = pn.dataclass.ModelViewer(
    model=leaflet_map, names=("center",), sizing_mode="stretch_both"
)
```

The `names` argument can also be a dictionary mapping trait names to parameter names.

## Create a Viewer from an ipywidget Class

To create a `Viewer` class from an ipywidget class, use the `ModelViewer` class:

```{pyodide}
import panel as pn
import ipyleaflet as ipyl
import param

pn.extension("ipywidgets")

class MapViewer(pn.dataclass.ModelViewer):
    _model_class = ipyl.Map
    _model_names = ["center", "zoom"]

    zoom = param.Number(4, bounds=(0, 24), step=1)

viewer = MapViewer(sizing_mode="stretch_both")

pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
```

The `_model_names` attribute is an optional iterable or dictionary. It specifies which traits to synchronize to which parameters.

## Create Reactive Values from the Traits of an ipywidget

Use `to_rx` to create reactive values from the traits of an ipywidget.

```{pyodide}
import panel as pn
import ipyleaflet as ipyl

pn.extension("ipywidgets")

leaflet_map = ipyl.Map(zoom=4)
zoom, zoom_control = pn.dataclass.to_rx(
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
