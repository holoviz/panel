"""
Shared base classes and utilities for working with dataclasses like
models including ipywidgets and Pydantic.
"""
from inspect import isclass
from typing import Any, Iterable

import param

from param import Parameterized


def _to_tuple(
    bases: None | Parameterized | Iterable[Parameterized],
) -> tuple[Parameterized]:
    if not bases:
        bases = ()
    if isclass(bases) and issubclass(bases, Parameterized):
        bases = (bases,)
    return tuple(bases)


class ModelUtils:
    """An abstract base class"""
    can_observe_field: bool = False

    supports_constant_fields = True

    _model_cache: dict[Any, Parameterized] = {}

    @classmethod
    def get_public_and_relevant_field_names(cls, model) -> tuple[str]:
        return tuple(
            name
            for name in cls.get_field_names(model)
            if cls.is_relevant_field_name(name)
        )

    @classmethod
    def ensure_dict(cls, names: Iterable[str] | dict[str, str] = ()) -> dict[str, str]:
        if isinstance(names, dict):
            return names
        return dict(zip(names, names))

    @classmethod
    def ensure_names_exists(
        cls, model, parameterized, names: dict[str, str]
    ) -> dict[str, str]:
        return {
            field: parameter
            for field, parameter in names.items()
            if field in cls.get_field_names(model) and parameter in parameterized.param
        }

    @classmethod
    def clean_names(
        cls, model, parameterized, names: Iterable[str] | dict[str, str]
    ) -> dict[str, str]:
        if isinstance(names, str):
            names=(names,)
        if not names:
            names = cls.get_public_and_relevant_field_names(model)
        names = cls.ensure_dict(names)
        return cls.ensure_names_exists(model, parameterized, names)

    @classmethod
    def get_field_names(cls, model) -> Iterable[str]:
        raise NotImplementedError()

    @classmethod
    def is_relevant_field_name(cls, name: str):
        if name.startswith("_"):
            return False
        return True

    @classmethod
    def sync_from_field_to_parameter(
        cls,
        model,
        field: str,
        parameterized: Parameterized,
        parameter: str,
    ):
        pass

    @classmethod
    def observe_field(
        cls,
        model,
        field: str,
        handle_change,
    ):
        raise NotImplementedError()

    @classmethod
    def create_parameterized(
        cls,
        model,
        names,
        bases,
    ):
        if not names:
            names = cls.get_public_and_relevant_field_names(model)
        names = cls.ensure_dict(names)
        bases = _to_tuple(bases)
        if not any(issubclass(base, Parameterized) for base in bases):
            bases += (Parameterized,)
        name = type(model).__name__
        key = (name, tuple(names.items()), bases)
        if name in cls._model_cache:
            parameterized = cls._model_cache[key]
        else:
            existing_params = ()
            for base in bases:
                if issubclass(base, Parameterized):
                    existing_params += tuple(base.param)
            params = {
                name: cls.create_parameter(model, field)
                for field, name in names.items()
                if name not in existing_params
            }
            parameterized = param.parameterized_class(name, params=params, bases=bases)
            parameterized._model__initialized = True
            cls._model_cache[key] = parameterized
        return parameterized

    @classmethod
    def create_parameter(
        cls,
        model,
        field,
    ) -> param.Parameter:
        return param.Parameter()

    @classmethod
    def sync_with_parameterized(
        cls,
        model,
        parameterized: Parameterized,
        names: Iterable[str] | dict[str, str] = (),
    ):
        names = cls.clean_names(model, parameterized, names)
        parameters = []
        mapping = {}

        for field, parameter in names.items():
            if parameter not in mapping:
                mapping[parameter] = []
            mapping[parameter].append(field)
            parameters.append(parameter)

            field_value = getattr(model, field)
            parameter_value = getattr(parameterized, parameter)

            if parameter_value is not None and parameter != 'name':
                try:
                    setattr(model, field, parameter_value)
                except Exception:
                    with param.edit_constant(parameterized):
                        setattr(parameterized, parameter, field_value)
            else:
                with param.edit_constant(parameterized):
                    setattr(parameterized, parameter, field_value)

            def _handle_field_change(
            _,
                model=model,
                field=field,
                parameterized=parameterized,
                parameter=parameter,
            ):
                with param.edit_constant(parameterized):
                    setattr(parameterized, parameter, getattr(model, field))
            cls.observe_field(model, field, _handle_field_change)

        def _handle_parameter_change(*events, read_only_fields: set[str] = set()):
            for e in events:
                fields = mapping[e.name]
                for field in fields:
                    if field in read_only_fields:
                        continue
                    try:
                        setattr(model, field, e.new)
                    except Exception:
                        read_only_fields.add(field)
        parameterized.param._watch(_handle_parameter_change, parameters, precedence=-1)

    @classmethod
    def get_layout(cls, model, self, layout_params):
        raise NotImplementedError()

    @classmethod
    def adjust_sizing(cls, self):
        pass

    @classmethod
    def get_required_defaults(cls, model_class):
        """Returns the default values of the fields that are required"""
        raise NotImplementedError()

class VariableLengthTuple(param.Parameter):
    """
    A non-fixed length Tuple parameter

    See https://github.com/holoviz/param/issues/955
    """

    def __init__(self, default=None, allow_None=True, **params):
        super().__init__(default=default, allow_None=allow_None, **params)
        self._validate(default)

    def _validate_value(self, val, allow_None):
        if val is None and allow_None:
            return
        if not isinstance(val, tuple):
            raise ValueError(
                f'VariableLengthTuple parameter {self.name!r} only takes '
                f'tuple values, not values of not {type(val)!r}.'
            )

    def _validate(self, val):
        self._validate_value(val, self.allow_None)

    @classmethod
    def serialize(cls, value):
        if value is None:
            return 'null'
        return list(value) if isinstance(value, tuple) else value

    @classmethod
    def deserialize(cls, value):
        if value == 'null':
            return None
        return tuple(value) if isinstance(value, list) else value
