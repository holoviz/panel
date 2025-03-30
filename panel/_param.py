from __future__ import annotations

from typing import (
    Any, Literal, TypeAlias, cast,
)

from bokeh.core.enums import enumeration
from param import Parameter, _is_number

AlignmentType = Literal["auto", "start", "center", "end"]
Alignment = enumeration(AlignmentType)
MarginType: TypeAlias = int | tuple[int, int] | tuple[int, int, int, int]


class Align(Parameter):
    """
    A Parameter type to validate alignment options. Supports 'auto', 'start',
    'center', 'end' or a two-tuple of these values corresponding
    to the (vertical, horizontal) alignment.
    """

    def __init__(
        self,
        default: AlignmentType | tuple[AlignmentType, AlignmentType] = "start",
        **params: Any
    ):
        super().__init__(default=default, **params)
        self._validate(default)

    def _validate(self, val: Any) -> None:
        self._validate_value(val, self.allow_None)

    def _validate_value(self, val: Any, allow_None: bool) -> None:
        if ((val is None and allow_None) or val in Alignment or
            (isinstance(val, tuple) and len(val) == 2 and all(v in Alignment for v in val))):
            return
        raise ValueError(
            f"Align parameter {self.name!r} must be one of 'start', "
            "'center', 'end' or a two-tuple specifying the (vertical, "
            f"horizontal) values for the alignment, not {val!r}."
        )


class Aspect(Parameter):
    """
    A Parameter type to validate aspect ratios. Supports numeric values
    and auto.
    """

    def __init__(self, default=None, allow_None=True, **params):
        super().__init__(default=default, allow_None=allow_None, **params)
        self._validate(default)

    def _validate(self, val: Any) -> None:
        self._validate_value(val, self.allow_None)

    def _validate_value(self, val: Any, allow_None: bool) -> None:
        if (val is None and allow_None) or val == 'auto' or _is_number(val):
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

    def _validate_value(self, val: Any, allow_None: bool) -> None:
        if val is None and allow_None:
            return
        if not isinstance(val, (tuple, int)):
            raise ValueError(
                f'Margin parameter {self.name!r} only takes integer and '
                f'tuple values, not values of not {type(val)!r}.'
            )

    def _validate_length(self, val: Any) -> None:
        if not isinstance(val, tuple) or len(val) in (2, 4):
            return
        raise ValueError(
            f'Margin parameter {self.name!r} only takes integer and '
            f'tuple values of length 2 (vertical, horizontal) or 4 '
            '(top, right, bottom, left).'
        )

    def _validate(self, val: Any) -> None:
        self._validate_value(val, self.allow_None)
        self._validate_length(val)

    @classmethod
    def serialize(cls, value: MarginType) -> Literal['null'] | list[int] | int:
        if value is None:
            return 'null'
        return list(value) if isinstance(value, tuple) else value

    @classmethod
    def deserialize(cls, value: Literal['null'] | list[int] | int) -> MarginType | None:
        if value == 'null':
            return None
        elif isinstance(value, list):
            n = len(value)
            if (n < 2 or n > 5):
                raise ValueError(f'Cannot deserialize list of length {n}.')
            return cast(MarginType, tuple(value))
        return value
