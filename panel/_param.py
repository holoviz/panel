from __future__ import annotations

import typing as t

from bokeh.core.enums import enumeration
from param import Parameter, _is_number

AlignmentType = t.Literal["auto", "start", "center", "end"]
Alignment = enumeration(AlignmentType)
MarginType: t.TypeAlias = int | tuple[int, int] | tuple[int, int, int, int]


class Align(Parameter):
    """
    A Parameter type to validate alignment options. Supports 'auto', 'start',
    'center', 'end' or a two-tuple of these values corresponding
    to the (vertical, horizontal) alignment.
    """

    def __init__(
        self,
        default: AlignmentType | tuple[AlignmentType, AlignmentType] = "start",
        **params: t.Any
    ):
        super().__init__(default=default, **params)
        self._validate(default)

    def _validate(self, val: t.Any) -> None:
        self._validate_value(val, self.allow_None)

    def _validate_value(self, value: t.Any, allow_None: bool) -> None:
        if ((value is None and allow_None) or value in Alignment or
            (isinstance(value, tuple) and len(value) == 2 and all(v in Alignment for v in value))):
            return
        raise ValueError(
            f"Align parameter {self.name!r} must be one of 'start', "
            "'center', 'end' or a two-tuple specifying the (vertical, "
            f"horizontal) values for the alignment, not {value!r}."
        )


class Aspect(Parameter):
    """
    A Parameter type to validate aspect ratios. Supports numeric values
    and auto.
    """

    def __init__(self, default=None, allow_None=True, **params):
        super().__init__(default=default, allow_None=allow_None, **params)
        self._validate(default)

    def _validate(self, val: t.Any) -> None:
        self._validate_value(val, self.allow_None)

    def _validate_value(self, value: t.Any, allow_None: bool) -> None:
        if (value is None and allow_None) or value == 'auto' or _is_number(value):
            return
        raise ValueError(
            f"Aspect parameter {self.name!r} only takes numeric values "
            "or the literal 'auto'."
        )


class Margin(Parameter):
    """
    A Parameter type to validate margins. Following CSS conventions
    the parameter supports numeric values and tuples of length 2 and 4
    corresponding to (vertical, horizontal) margins and (top, right,
    bottom, left) margins.
    """

    def __init__(self, default=None, allow_None=True, **params):
        super().__init__(default=default, allow_None=allow_None, **params)
        self._validate(default)

    def _validate_value(self, value: t.Any, allow_None: bool) -> None:
        if value is None and allow_None:
            return
        if not isinstance(value, (tuple, int)):
            raise ValueError(
                f'Margin parameter {self.name!r} only takes integer and '
                f'tuple values, not values of not {type(value)!r}.'
            )

    def _validate_length(self, value: t.Any) -> None:
        if not isinstance(value, tuple) or len(value) in (2, 4):
            return
        raise ValueError(
            f'Margin parameter {self.name!r} only takes integer and '
            f'tuple values of length 2 (vertical, horizontal) or 4 '
            '(top, right, bottom, left).'
        )

    def _validate(self, val: t.Any) -> None:
        self._validate_value(val, self.allow_None)
        self._validate_length(val)

    @classmethod
    def serialize(cls, value: MarginType) -> t.Literal['null'] | list[int] | int:
        if value is None:
            return 'null'
        return list(value) if isinstance(value, tuple) else value

    @classmethod
    def deserialize(cls, value: t.Literal['null'] | list[int] | int) -> MarginType | None:
        if value == 'null':
            return None
        elif isinstance(value, list):
            n = len(value)
            if (n < 2 or n > 5):
                raise ValueError(f'Cannot deserialize list of length {n}.')
            return t.cast("MarginType", tuple(value))
        return value
