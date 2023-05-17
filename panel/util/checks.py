from __future__ import annotations

import datetime as dt
import os
import sys

from typing import Any, Iterable

import numpy as np
import param

__all__ = (
    "datetime_types",
    "is_dataframe",
    "is_holoviews",
    "is_number",
    "is_parameterized",
    "is_series",
    "isdatetime",
    "isfile",
    "isIn",
    "isurl",
)


datetime_types = (np.datetime64, dt.datetime, dt.date)


def isfile(path: str) -> bool:
    """Safe version of os.path.isfile robust to path length issues on Windows"""
    try:
        return os.path.isfile(path)
    except (TypeError, ValueError): # path too long for Windows
        return False


def isurl(obj: Any, formats: Iterable[str] | None = None) -> bool:
    if not isinstance(obj, str):
        return False
    lower_string = obj.lower().split('?')[0].split('#')[0]
    return (
        lower_string.startswith('http://')
        or lower_string.startswith('https://')
    ) and (formats is None or any(lower_string.endswith('.'+fmt) for fmt in formats))


def is_dataframe(obj) -> bool:
    if 'pandas' not in sys.modules:
        return False
    import pandas as pd
    return isinstance(obj, pd.DataFrame)


def is_series(obj) -> bool:
    if 'pandas' not in sys.modules:
        return False
    import pandas as pd
    return isinstance(obj, pd.Series)


def isIn(obj, objs):
    """
    Checks if the object is in the list of objects safely.
    """
    for o in objs:
        if o is obj:
            return True
        try:
            if o == obj:
                return True
        except Exception:
            pass
    return False


def is_parameterized(obj) -> bool:
    """
    Whether an object is a Parameterized class or instance.
    """
    return (isinstance(obj, param.Parameterized) or
            (isinstance(obj, type) and issubclass(obj, param.Parameterized)))


def is_holoviews(obj: Any) -> bool:
    """
    Whether the object is a HoloViews type that can be rendered.
    """
    if 'holoviews' not in sys.modules:
        return False
    from holoviews.core.dimension import Dimensioned
    from holoviews.plotting import Plot
    return isinstance(obj, (Dimensioned, Plot))


def isdatetime(value) -> bool:
    """
    Whether the array or scalar is recognized datetime type.
    """
    if is_series(value) and len(value):
        return isinstance(value.iloc[0], datetime_types)
    elif isinstance(value, np.ndarray):
        return (
            value.dtype.kind == "M" or
            (value.dtype.kind == "O" and len(value) != 0 and
             isinstance(value[0], datetime_types))
        )
    elif isinstance(value, list):
        return all(isinstance(d, datetime_types) for d in value)
    else:
        return isinstance(value, datetime_types)


def is_number(s: Any) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False
