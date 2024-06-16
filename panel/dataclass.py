"""Functionality to enable easy interaction with dataclass like instances or classes via familiar APIs from Param like watch, bind, depends, and rx.

## Libraries Supported

- **Traitlets**: A library for creating dataclass like models (`HasTraits`) with observable fields (called *traits*).
- **ipywidgets**: A library for creating interactive widgets for notebooks. Its base class `Widget` derives from `HasTraitlets`.

In the future dataclasses, Pydantic or other dataclass like libraries may be supported.

## Terminology

- **Param**: A library for creating dataclass like models (`Parameterized`) with watchable attributes (called *parameters*).
- **model**: A child class of one of the libraries listed above.
- **fields**: The attributes of the model class or instance. Derives from `dataclass.field()`.
- **names**: The names of the model attributes/ Parameterized parameters.

## Classes

- `ModelParameterized`: An abstract Parameterized base class for observing a model class or instance.
- `ModelViewer`: An abstract Layoutable Viewer base class for observing a model class or instance.

## Functions

- `create_rx`: Creates `rx` values from fields of a model.
- `sync_with_parameterized`: Syncs the fields of a model with the parameters of a Parameterized object.
- `sync_with_widget`: Syncs an iterable or dictionary of named fields of a model with the named parameters of a Parameterized object.
- `sync_with_rx`: Syncs a single field of a model with an `rx` value.

## Support

| Library | Sync Model -> Parameterized | Sync Parameterized -> Model | `create_rx` | `sync_with_parameterized` | `sync_with_widget` | `sync_with_rx` | `ModelParameterized` | `ModelViewer` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Traitlets | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| ipywidgets | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

""" # noqa: E501

from ._dataclasses.ipywidget import (
    ModelParameterized, ModelViewer, create_rx, sync_with_parameterized,
    sync_with_rx, sync_with_widget,
)

__all__=["create_rx", "sync_with_parameterized", "sync_with_widget", "sync_with_rx", "ModelParameterized", "ModelViewer"]
