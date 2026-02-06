import datetime as dt
import json

from collections.abc import Callable
from typing import (
    TYPE_CHECKING, Any, Iterable, Literal,
)

import param

from param.reactive import bind

from ..pane.markup import JSON
from ..util import classproperty
from .base import ModelUtils, VariableLengthTuple

if TYPE_CHECKING:
    try:
        from pydantic import BaseModel
    except ModuleNotFoundError:
        BaseModel = Any
else:
    BaseModel = Any

def _default_serializer(obj):
    if isinstance(obj, (dt.datetime, dt.date)):
        return obj.isoformat()
    if isinstance(obj, bytes):
        return obj.decode(encoding='utf-8')
    if isinstance(obj, Callable):
        return str(obj)
    raise TypeError(f"Cannot serialize {obj!r} (type {type(obj)})")


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

    @classproperty
    def parameter_map(cls):
        return {
            bool: param.Boolean,
            bytes: param.Bytes,
            Callable: param.Callable,
            dict: param.Dict,
            Literal: param.Selector,
            float: param.Number,
            int: param.Integer,
            list: param.List,
            str: param.String,
            tuple: VariableLengthTuple,
        }

    @classmethod
    def create_parameter(cls, model, field: str)->param.Parameter:
        field_info = model.model_fields[field]
        field_type = field_info.annotation
        kwargs={"doc": field_info.description}

        if hasattr(field_type, '__origin__'):
            ptype = cls.parameter_map.get(field_type.__origin__, param.Parameter)
            if ptype is param.Selector and hasattr(field_type, '__args__'):
                kwargs["objects"] = list(field_type.__args__)
        else:
            ptype = cls.parameter_map.get(field_type, param.Parameter)

        if hasattr(model, field):
            kwargs['default'] = getattr(model, field)

        return ptype(
            **kwargs
        )

    @classmethod
    def get_layout(cls, model, self, layout_params):
        def view_model(*args):
            if hasattr(model, 'model_dump'):
                return model.model_dump()
            else:
                return json.loads(model.json())

        return JSON(
            bind(view_model, *self.param.objects().values()),
            default=_default_serializer,
            depth=2,
            **layout_params
        )

    @classmethod
    def get_required_defaults(cls, model_class):
        return {field: cls.create_parameter(model_class, field).default for field, info in model_class.model_fields.items() if info.is_required()}
