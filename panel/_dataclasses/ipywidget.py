"""Functionality to enable easy interaction with Traitlets models and ipywidgets via familiar APIs from Param like watch, bind, depends, and rx.

## Terminology

- **Traitlets**: A library for creating classes (`HasTraits`) with observable attributes (called *traits*).
- **Param**: A library similar to Traitlets, for creating classes (`Parameterized`) with watchable attributes (called *parameters*).
- **ipywidgets**: Builds on Traitlets to create interactive widgets for Jupyter notebooks.
- **widget**: Refers to ipywidgets.
- **model**: Refers to Traitlets classes including ipywidgets.

## Classes

- `ModelParameterized`: An abstract Parameterized base class for wrapping a traitlets HasTraits class or instance.
- `ModelViewer`: An abstract base class for creating a Layoutable Viewer that wraps an ipywidget Widget class or instance.

## Functions

- `create_rx`: Creates `rx` values from traits of a model, each synced to a trait of the model.
- `sync_with_widget`: Syncs the named trait of the model with the value of a Panel widget.
- `sync_with_parameterized`: Syncs the traits of a model with the parameters of a Parameterized object.
- `sync_with_rx`: Syncs a single trait of a model with an `rx` value.

All synchronization is bidirectional. We only synchronize the top-level traits/ parameters and not the nested ones.
"""

# I've tried to implement this in a way that would generalize to similar APIs for other *dataclass like* libraries like dataclasses, Pydantic, attrs etc.

from typing import TYPE_CHECKING, Any, Iterable

from ..pane.ipywidget import IPyWidget
from .base import ModelUtils

if TYPE_CHECKING:
    try:
        from traitlets import HasTraits
    except ModuleNotFoundError:
        HasTraits = Any

    try:
        from ipywidgets import Widget
    except ModuleNotFoundError:
        Widget = Any
else:
    HasTraits = Any
    Widget = Any

class TraitletsUtils(ModelUtils):
    can_observe_field = True

    @classmethod
    def get_field_names(cls, model: HasTraits)->Iterable[str]:
        return model.traits()

    @classmethod
    def observe_field(
        cls,
        model,
        field: str,
        handle_change,
    ):
        # We don't know if this is possible
        model.observe(handle_change, names=field)

    @classmethod
    def is_relevant_field_name(cls, name: str):
        if name in {"comm", "tabbable", "keys", "log", "layout"}:
            return False
        return super().is_relevant_field_name(name)

    @classmethod
    def get_layout(cls, model, self, layout_params):
        if hasattr(model, "layout"):
            model.layout.height = "100%"
            model.layout.width = "100%"

        return IPyWidget(model, **layout_params)

    @classmethod
    def adjust_sizing(cls, parameterized):
        if not parameterized.width and parameterized.sizing_mode not in ["stretch_width", "stretch_both"]:
            parameterized.width = 300

        if not parameterized.height and parameterized.sizing_mode not in [
            "stretch_height",
            "stretch_both",
        ]:
            parameterized.height = 300