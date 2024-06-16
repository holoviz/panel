import json

from asyncio import sleep
from typing import TYPE_CHECKING, Any, Iterable

from param.reactive import bind

from ..pane.markup import JSON
from .base import ModelUtils

if TYPE_CHECKING:
    try:
        from pydantic import BaseModel
    except ModuleNotFoundError:
        BaseModel = Any
else:
    BaseModel = Any


class PydanticUtils(ModelUtils):
    can_observe_field = False
    supports_constant_fields = False

    # Todo: Fix issue and remove this hack
    _is_testing = False

    @classmethod
    def get_field_names(cls, model: BaseModel) -> Iterable[str]:
        return tuple(model.model_fields)

    @classmethod
    def observe_field(
        cls,
        model,
        field: str,
        handle_change,
    ):
        # We don't know if this is possible
        pass

    @classmethod
    def get_layout(cls, model, self, layout_params):
        # Todo: Find proper solution to update the layout after the model is updated
        # Hack: For some reason the model is updated after the UI is rendered
        # We might setup a callback to update the layout below after the model is updated
        async def view_model(*args, model=model):
            if not cls._is_testing:
                await sleep(0.250)
            return json.loads(model.json())

        parameters = [
            parameter
            for name, parameter in self.param.params().items()
            if name not in layout_params
        ]
        parameters = []
        iview = bind(view_model, *parameters)

        return JSON(iview, depth=2, **layout_params)
