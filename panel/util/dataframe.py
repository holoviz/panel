"""
Backend neutral helpers for tabular data.

Panel's data components historically assume pandas. pandas-like frames
(pandas, modin, cuDF) carry a row index which Panel uses to identify
rows across filtering, sorting and editing. Other DataFrame libraries
supported by Narwhals, e.g. Polars and PyArrow, have no such index, so
for those Panel identifies a row by its position in the original frame
and tracks it through filtering and sorting using a temporary row index
column (see `ROW_INDEX`).

Write operations never mutate these frames in place, since some
backends (e.g. PyArrow) are immutable. Instead a new frame is built
and the component's value is replaced.

Narwhals is imported inside the functions to avoid adding to the
import time of Panel.
"""
from __future__ import annotations

import datetime as dt
import typing as t

from collections.abc import Iterable, Mapping, Sequence

import numpy as np

if t.TYPE_CHECKING:
    import narwhals.stable.v2 as nw

ROW_INDEX = '__panel_row_index__'


def has_index(obj: t.Any) -> bool:
    """
    Whether the object is a pandas-like DataFrame, which carries a row
    index that can label rows.
    """
    if obj is None or isinstance(obj, dict):
        return False
    import narwhals.stable.v2.dependencies as nwd
    return nwd.is_pandas_like_dataframe(obj)


def is_dataframe(obj: t.Any) -> bool:
    """
    Whether the object is an eager DataFrame from any library supported
    by Narwhals, e.g. pandas, Polars or PyArrow.
    """
    if obj is None or isinstance(obj, (dict, list, str)):
        return False
    import narwhals.stable.v2.dependencies as nwd
    return nwd.is_into_dataframe(obj)


def is_indexless(obj: t.Any) -> bool:
    """
    Whether the object is a DataFrame without a row index, e.g. a Polars
    DataFrame or a PyArrow Table.
    """
    return is_dataframe(obj) and not has_index(obj)


def to_narwhals(obj: t.Any) -> nw.DataFrame[t.Any]:
    """
    Wraps a native DataFrame in a Narwhals DataFrame without copying.
    """
    import narwhals.stable.v2 as nw
    return nw.from_native(obj, eager_only=True)


def to_native(df: t.Any) -> t.Any:
    import narwhals.stable.v2 as nw
    return nw.to_native(df) if isinstance(df, nw.DataFrame) else df


def column_names(obj: t.Any) -> list[t.Any]:
    """
    Returns the column names of a dictionary of columns or DataFrame.
    """
    if isinstance(obj, dict):
        return list(obj)
    elif has_index(obj):
        return list(obj.columns)
    return to_narwhals(obj).columns


def copy_data(obj: t.Any) -> t.Any:
    """
    Copies data which may be mutated in place, i.e. dictionaries and
    pandas-like DataFrames. Other DataFrames are never mutated so they
    are returned as is.
    """
    if isinstance(obj, dict) or has_index(obj):
        return obj.copy()
    return obj


def dtype_kind(dtype: nw.dtypes.DType) -> str:
    """
    Maps a Narwhals dtype onto the equivalent NumPy dtype kind.
    """
    import narwhals.stable.v2 as nw
    if dtype == nw.Boolean:
        return 'b'
    elif dtype.is_signed_integer():
        return 'i'
    elif dtype.is_unsigned_integer():
        return 'u'
    elif dtype.is_float() or dtype == nw.Decimal:
        return 'f'
    elif dtype == nw.Datetime or dtype == nw.Date:
        return 'M'
    elif dtype == nw.Duration:
        return 'm'
    elif dtype in (nw.String, nw.Categorical, nw.Enum):
        return 'U'
    return 'O'


def is_date(dtype: nw.dtypes.DType) -> bool:
    import narwhals.stable.v2 as nw
    return dtype == nw.Date


def add_row_index(obj: t.Any, offset: int = 0) -> t.Any:
    """
    Adds a column recording the position of each row, so rows can be
    tracked through filtering and sorting.
    """
    import narwhals.stable.v2 as nw
    df = to_narwhals(obj).with_row_index(ROW_INDEX)
    if offset:
        df = df.with_columns(nw.col(ROW_INDEX) + offset)
    return df.to_native()


def drop_row_index(obj: t.Any) -> t.Any:
    df = to_narwhals(obj)
    if ROW_INDEX in df.columns:
        df = df.drop(ROW_INDEX)
    return df.to_native()


def row_positions(obj: t.Any) -> list[int]:
    """
    Returns the positions of the rows in the original frame, as
    recorded by `add_row_index`.
    """
    return to_narwhals(obj)[ROW_INDEX].to_list()


def take_rows(obj: t.Any, rows: Sequence[int] | slice) -> t.Any:
    df = to_narwhals(obj)
    if isinstance(rows, slice):
        return df[rows].to_native()
    return df[list(rows)].to_native()


def filter_rows(obj: t.Any, mask: np.ndarray) -> t.Any:
    return to_narwhals(obj).filter(np.asarray(mask, dtype=bool).tolist()).to_native()


def row_dict(obj: t.Any, row: int) -> dict[str, t.Any]:
    """
    Returns a row as a dictionary of column name to value, omitting
    the row index column.
    """
    return to_narwhals(drop_row_index(obj))[row:row+1].rows(named=True)[0]


def column_to_numpy(obj: t.Any, column: str) -> np.ndarray:
    return to_narwhals(obj)[column].to_numpy()


def to_column_data(obj: t.Any) -> dict[str, np.ndarray]:
    """
    Converts a DataFrame into a dictionary of NumPy arrays, which can
    be sent to a ColumnDataSource.
    """
    df = to_narwhals(obj)
    data = {}
    for col in df.columns:
        if col == ROW_INDEX:
            continue
        array = df[col].to_numpy()
        if array.dtype.kind in 'SU':
            # Fixed width strings would truncate longer values patched in
            array = array.astype(object)
        data[col] = array
    return data


def _to_series(name: str, values: t.Any, dtype: t.Any, backend: t.Any) -> nw.Series[t.Any]:
    import narwhals.stable.v2 as nw
    try:
        return nw.new_series(name, values, dtype, backend=backend)
    except Exception:
        # Values coming from the frontend may not be directly castable,
        # e.g. integer columns with missing values arrive as floats
        # with NaNs.
        values = [
            None if isinstance(v, float) and np.isnan(v) else v
            for v in np.asarray(values).tolist()
        ]
        return nw.new_series(name, values, backend=backend).cast(dtype)


def set_values(obj: t.Any, column: str, rows: Sequence[int], values: t.Any) -> t.Any:
    """
    Returns a new frame with the values of the column at the supplied
    row positions replaced.
    """
    df = to_narwhals(obj)
    series = df[column]
    rows = list(rows)
    if len(rows) == len(df) and rows == list(range(len(df))):
        new = _to_series(column, values, series.dtype, df.implementation)
    else:
        new = series.scatter(rows, _to_series(column, values, series.dtype, df.implementation))
    return df.with_columns(new).to_native()


def frame_from_columns(data: Mapping[str, t.Any], template: t.Any) -> t.Any:
    """
    Builds a frame from a dictionary of columns using the backend of
    the template frame.
    """
    import narwhals.stable.v2 as nw
    impl = to_narwhals(template).implementation
    return nw.from_dict({str(k): list(v) for k, v in data.items()}, backend=impl).to_native()


def _is_scalar(value: t.Any) -> bool:
    return np.isscalar(value) or value is None or isinstance(value, (dt.date, dt.time, np.datetime64))


def coerce_frame(value: t.Any, template: t.Any) -> t.Any:
    """
    Converts a DataFrame, Series or dictionary of rows or columns into a
    frame of the same backend and schema as the template frame.
    """
    import narwhals.stable.v2 as nw
    tmpl = to_narwhals(template)
    impl = tmpl.implementation
    if hasattr(value, 'to_dict') and not is_dataframe(value) and not isinstance(value, dict):
        # A pandas Series represents a single row
        value = value.to_dict()
    if isinstance(value, Mapping):
        if all(_is_scalar(v) for v in value.values()):
            value = {k: [v] for k, v in value.items()}
        df = nw.from_dict({str(k): list(v) for k, v in value.items()}, backend=impl)
    elif is_dataframe(value):
        df = to_narwhals(value)
        if has_index(value):
            df = to_narwhals(value.reset_index(drop=True))
        if df.implementation != impl:
            df = nw.from_dict(df.to_dict(as_series=False), backend=impl)
    else:
        raise ValueError(
            f"Cannot convert value of type {type(value).__name__} into a "
            "DataFrame, provide a DataFrame or dictionary."
        )
    schema = tmpl.schema
    return df.select([
        nw.col(col).cast(dtype) if col in df.columns else nw.lit(None).cast(dtype).alias(col)
        for col, dtype in schema.items()
    ]).to_native()


def concat_rows(obj: t.Any, other: t.Any, rollover: int | None = None) -> t.Any:
    import narwhals.stable.v2 as nw
    df = nw.concat([to_narwhals(obj), to_narwhals(other)], how='vertical')
    if rollover is not None:
        df = df.tail(rollover)
    return df.to_native()


def _filter_value(value: t.Any, kind: str) -> t.Any:
    if kind in 'iufb' and not isinstance(value, (list, tuple, set, np.ndarray)):
        dtype = np.dtype({'i': 'int64', 'u': 'uint64', 'f': 'float64', 'b': 'bool'}[kind])
        return dtype.type(value).item()
    return value


def filter_masks(
    obj: t.Any, filters: Iterable[tuple[str, t.Any]]
) -> list[np.ndarray]:
    """
    Computes boolean masks for (column, value) filters, where the value
    is a scalar (equality), a list or set (membership) or a tuple
    (inclusive range).
    """
    import narwhals.stable.v2 as nw
    df = to_narwhals(obj)
    exprs = []
    for col_name, val in filters:
        col = nw.col(col_name)
        if val is None:
            continue
        elif np.isscalar(val):
            expr = col == val
        elif isinstance(val, (list, set)):
            if not val:
                continue
            expr = col.is_in(list(val))
        elif isinstance(val, tuple):
            start, end = val
            if start is None and end is None:
                continue
            elif start is None:
                expr = col <= end
            elif end is None:
                expr = col >= start
            else:
                expr = (col >= start) & (col <= end)
        else:
            raise ValueError(f"'{col_name} filter value not "
                             "understood. Must be either a scalar, "
                             "tuple or list.")
        exprs.append(expr)
    return _evaluate(df, exprs)


def header_filter_masks(
    obj: t.Any, filters: Iterable[Mapping[str, t.Any]],
    filter_defs: Mapping[str, t.Any] | None = None
) -> list[np.ndarray]:
    """
    Computes boolean masks for Tabulator header filter specifications,
    each declaring a 'field', 'type' and 'value'.
    """
    import narwhals.stable.v2 as nw
    df = to_narwhals(obj)
    filter_defs = filter_defs or {}
    exprs = []
    for filt in filters:
        col_name = filt['field']
        op = filt['type']
        val = filt['value']
        if col_name not in df.columns:
            continue

        # Sometimes Tabulator will provide a zero/single element list
        if isinstance(val, list):
            if len(val) == 1:
                val = val[0]
            elif not val:
                continue

        col = nw.col(col_name)
        val = _filter_value(val, dtype_kind(df.schema[col_name]))
        text = col.cast(nw.String).str.to_lowercase()
        if op == '=':
            expr = col == val
        elif op == '!=':
            expr = col != val
        elif op == '<':
            expr = col < val
        elif op == '>':
            expr = col > val
        elif op == '>=':
            expr = col >= val
        elif op == '<=':
            expr = col <= val
        elif op == 'in':
            if not isinstance(val, (list, np.ndarray)):
                val = [val]
            expr = col.is_in(list(val))
        elif op == 'like':
            expr = text.str.contains(str(val).lower(), literal=True)
        elif op == 'starts':
            expr = text.str.starts_with(str(val).lower())
        elif op == 'ends':
            expr = text.str.ends_with(str(val).lower())
        elif op == 'keywords':
            match_all = filter_defs.get(col_name, {}).get('matchAll', False)
            sep = filter_defs.get(col_name, {}).get('separator', ' ')
            matches = [
                text.str.contains(match.lower(), literal=True)
                for match in str(val).split(sep)
            ]
            if match_all:
                exprs.extend(matches)
                continue
            expr = matches[0]
            for match in matches[1:]:
                expr = expr | match
        elif op == 'regex':
            raise ValueError("Regex filtering not supported.")
        else:
            raise ValueError(f"Filter type {op!r} not recognized.")
        exprs.append(expr)
    return _evaluate(df, exprs)


def _evaluate(df: nw.DataFrame[t.Any], exprs: list[nw.Expr]) -> list[np.ndarray]:
    if not exprs:
        return []
    masks = df.select([
        expr.fill_null(False).alias(f'_mask_{i}') for i, expr in enumerate(exprs)
    ])
    return [masks[col].to_numpy().astype(bool) for col in masks.columns]


def sort_frame(obj: t.Any, fields: Sequence[str], ascending: Sequence[bool]) -> t.Any:
    """
    Sorts a frame mirroring the sorting algorithm of Tabulator, i.e.
    strings are compared case-insensitively with missing strings
    treated as empty, other missing values are placed last and ties
    are broken by the string representation of the row position.
    """
    import narwhals.stable.v2 as nw
    df = to_narwhals(obj)
    keys, exprs, descending = [], [], []
    for i, (field, asc) in enumerate(zip(fields, ascending, strict=True)):
        if field not in df.columns:
            continue
        kind = dtype_kind(df.schema[field])
        expr = nw.col(field)
        if kind == 'U':
            expr = expr.cast(nw.String).fill_null('').str.to_lowercase()
        elif kind == 'f':
            expr = expr.fill_nan(None)
        key = f'_sort_{i}_'
        keys.append(key)
        exprs.append(expr.alias(key))
        descending.append(not asc)
    if not keys:
        return df.to_native()
    tie = '_sort_tie_'
    sorted_df = (
        df.with_row_index(tie)
        .with_columns(nw.col(tie).cast(nw.String), *exprs)
        .sort([*keys, tie], descending=[*descending, False], nulls_last=True)
        .drop([*keys, tie])
    )
    return sorted_df.to_native()


__all__ = (
    "ROW_INDEX",
    "add_row_index",
    "column_names",
    "column_to_numpy",
    "concat_rows",
    "copy_data",
    "drop_row_index",
    "dtype_kind",
    "filter_masks",
    "filter_rows",
    "frame_from_columns",
    "has_index",
    "header_filter_masks",
    "is_dataframe",
    "is_date",
    "is_indexless",
    "row_dict",
    "row_positions",
    "set_values",
    "sort_frame",
    "take_rows",
    "to_column_data",
    "to_narwhals",
    "to_native",
)
