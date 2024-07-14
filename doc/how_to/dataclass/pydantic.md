# Interact with Pydantic

This how-to guide demonstrates how to easily enable interaction with [Pydantic](https://docs.pydantic.dev/latest/) using familiar APIs from Panel and [Param](https://param.holoviz.org/), such as `watch`, `bind`, `depends`, and `rx`.

## Overview

The `pn.dataclass` module provides functions to synchronize the fields of Pydantic `BaseModel` with a Parameterized object, a Panel widget, or an `rx` value. It also provides a `ModelViewer` class for creating a Layoutable Viewer that wraps an Pydantic `BaseModel` class or instance.

### Terminology

- **Pydantic**: A library for creating dataclass like models (`BaseModel`) with non-observable fields.
- **model**: Refers to Pydantic `BaseModel` classes and instances.
- **names**: Refers to the names of the fields/parameters to synchronize. Can be an iterable or a dictionary mapping from field names to parameter names.

### Classes

- **`ModelParameterized`**: An abstract Parameterized base class that can wrap a Pydantic `BaseModel` class or instance.
- **`ModelViewer`**: An abstract base class for creating a Layoutable Viewer that can wrap a Pydantic `BaseModel` class or instance.

### Functions

- **`to_rx`**: Can create `rx` values from fields of a model, synced to the fields of the model.
- **`sync_with_parameterized`**: Syncs the fields of a model with the parameters of a Parameterized object.
- **`sync_with_widget`**: Syncs a field of the model with the value of a Panel widget.
- **`sync_with_rx`**: Syncs a field of a model with an `rx` value.

All synchronization is from Parameterized to Pydantic model. The other way is currently not supported.

Only top-level fields/parameters are synchronized, not nested ones.

## Synchronize a Field of a model with a Panel Widget

Use `sync_with_widget` to synchronize a field of a model with the `value` parameter of a Panel widget.

```{pyodide}
import panel as pn
from datetime import datetime
from pydantic import BaseModel
import json

pn.extension()


class DeliveryModel(BaseModel):
    timestamp: datetime = datetime(2021, 1, 1, 1, 1, 1)

model = DeliveryModel()

widget = pn.widgets.DatetimeInput(name="Timestamp")
pn.dataclass.sync_with_widget(model, widget, "timestamp")

def view_model(*args):
    return json.loads(model.json())

pn.Column(
    widget,
    pn.pane.JSON(pn.bind(view_model, widget)),
).servable()
```

## Synchronize a model with a Parameterized Object

Use `sync_with_parameterized` to synchronize a model with a Parameterized object.

```{pyodide}
import panel as pn
from datetime import datetime
from pydantic import BaseModel
import json
import param

pn.extension()


class DeliveryModel(BaseModel):
    timestamp: datetime = datetime(2021, 1, 1, 1, 1, 1)
    dimensions: tuple[int, int] = (10, 10)


class DeliveryParameterized(param.Parameterized):
    timestamp = param.Date(datetime(2021, 2, 2, 2, 2, 2))
    dimensions = param.Tuple((20, 20))


model = DeliveryModel()
parameterized = DeliveryParameterized()

pn.dataclass.sync_with_parameterized(model, parameterized)


def view_model(*args):
    return json.loads(model.json())


pn.Column(
    parameterized.param,
    pn.pane.JSON(
        pn.bind(
            view_model, parameterized.param.timestamp, parameterized.param.dimensions
        ),
        depth=2,
    ),
).servable()
```

The `sync_with_parameterized` function synchronizes the shared fields/parameters `timestamp` and `dimensions` between the `model` and `parameterized` objects.

To specify a subset of fields/parameters to synchronize, use the `names` argument:

```python
pn.dataclass.sync_with_parameterized(
    model=model, parameterized=parameterized, names=("timestamp",)
)
```

The `names` argument can also be a dictionary mapping field names to parameter names:

```{pyodide}
import panel as pn
from datetime import datetime
from pydantic import BaseModel
import json
import param

pn.extension()

class DeliveryModel(BaseModel):
    timestamp: datetime = datetime(2021, 1, 1, 1, 1, 1)
    dimensions: tuple[int, int] = (10, 10)

class DeliveryParameterized(param.Parameterized):
    timestamp_value = param.Date(datetime(2021, 2, 2, 2, 2, 2))
    dimensions_value = param.Tuple((20, 20))

model = DeliveryModel()
parameterized = DeliveryParameterized()

pn.dataclass.sync_with_parameterized(
    model=model,
    parameterized=parameterized,
    names={"timestamp": "timestamp_value", "dimensions": "dimensions_value"},
)

def view_model(*args):
    return json.loads(model.json())

pn.Column(
    parameterized.param,
    pn.pane.JSON(
        pn.bind(
            view_model,
            parameterized.param.timestamp_value,
            parameterized.param.dimensions_value,
        ),
        depth=2,
    ),
).servable()
```

## Create a Viewer from a model Instance

To create a `Viewer` object from a model instance, use the `ModelViewer` class:

```{pyodide}
import panel as pn
from datetime import datetime
from pydantic import BaseModel

pn.extension()

class DeliveryModel(BaseModel):
    timestamp: datetime = datetime(2021, 1, 1, 1, 1, 1)
    dimensions: tuple[int, int] = (10, 10)

model = DeliveryModel()

viewer = pn.dataclass.ModelViewer(model=model, sizing_mode="stretch_both")
pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
```

Check out the parameters to the left of the JSON pane, there you will find all the fields of the `DeliveryModel` instance. Try changing some the `dimensions`.

To specify a subset of fields/parameters to synchronize, use the `names` argument:

```python
viewer = pn.dataclass.ModelViewer(
    model=model, names=("dimensions",), sizing_mode="stretch_both"
)
```

The `names` argument can also be a dictionary mapping field names to parameter names.

## Create a Viewer from a model Class

To create a `Viewer` class from a model class, use the `ModelViewer` class:

```{pyodide}
import panel as pn
from datetime import datetime
from pydantic import BaseModel
import param

pn.extension()


class DeliveryModel(BaseModel):
    timestamp: datetime = datetime(2021, 1, 1, 1, 1, 1)
    dimensions: tuple[int, int] = (10, 10)

class DeliveryViewer(pn.dataclass.ModelViewer):
    _model_class = DeliveryModel
    _model_names = ["timestamp", "dimensions"]

    timestamp = param.Date(datetime(2021, 2, 2, 2, 2, 2))
    dimensions = param.Tuple((20, 20))

viewer = DeliveryViewer(dimensions=(30,30), sizing_mode="stretch_both")
pn.Row(pn.Column(viewer.param, scroll=True), viewer, height=400).servable()
```

The `_model_names` attribute is an optional iterable or dictionary. It specifies which fields to synchronize to which parameters.

## Create a Reactive Value from the Field of a model

Use `to_rx` to create a reactive value from the field of a model.

```{pyodide}
import panel as pn
from datetime import datetime
from pydantic import BaseModel
import json

pn.extension()


class DeliveryModel(BaseModel):
    timestamp: datetime = datetime(2021, 1, 1, 1, 1, 1)
    dimensions: tuple[int, int] = (10, 10)

model = DeliveryModel()

timestamp, dimensions = pn.dataclass.to_rx(model, "timestamp", "dimensions")

timestamp_input = pn.widgets.DatetimeInput(name="Timestamp", value=model.timestamp)

def update_timestamp(value):
    timestamp.rx.value = value

    return json.loads(model.json())


pn.Row(
    pn.bind(update_timestamp, timestamp_input),
    timestamp_input, timestamp,
    height=400).servable()
```
