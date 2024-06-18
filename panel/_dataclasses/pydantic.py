import json

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
        # Maybe solution can be found in
        # https://github.com/pydantic/pydantic/discussions/7127 or
        # https://psygnal.readthedocs.io/en/latest/API/model/
        pass

    @classmethod
    def get_layout(cls, model, self, layout_params):
        exclude = list(layout_params)
        def view_model(*args):
            if hasattr(model, 'model_dump'):
                return model.model_dump(exclude=exclude)
            else:
                return json.loads(model.json(exclude=exclude))

        parameters = [
            parameter for name, parameter in self.param.objects().items()
            if name not in layout_params
        ]
        return JSON(bind(view_model, *parameters), depth=2, **layout_params)
