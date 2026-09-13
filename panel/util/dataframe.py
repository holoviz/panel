"""
Backend neutral helpers for tabular data.

Panel is increasingly handed DataFrames that are not pandas. Narwhals provides
a common API over them, and Bokeh already accepts any Narwhals compatible frame
as ColumnDataSource input, so code that needs to inspect or transform a frame
should come through here rather than reaching for pandas directly.

Narwhals is imported inside the functions rather than at module scope. It costs
roughly 40ms to import, `import panel` does not pay that today, and
`panel/pane/vega.py` already follows the same pattern.
"""
from __future__ import annotations

import typing as t

if t.TYPE_CHECKING:
    import narwhals.stable.v2 as nw

__all__ = (
    "has_index",
    "is_dataframe",
    "to_narwhals",
)


def has_index(obj: t.Any) -> bool:
    """
    Whether the frame carries a row index that can label rows.

    pandas and the libraries that copy its API have one, Polars and PyArrow
    do not. Code that addresses rows by label has to fall back to addressing
    them by position for the latter.
    """
    import narwhals.stable.v2 as nw
    return nw.dependencies.is_pandas_like_dataframe(obj)


def is_dataframe(obj: t.Any) -> bool:
    """
    Whether the object is an eager DataFrame from any library Narwhals
    supports, such as pandas, Polars or PyArrow.

    Note this is deliberately broader than `panel.util.checks.is_dataframe`,
    which answers the narrower question of whether the object is a pandas
    DataFrame specifically. Callers that go on to use the pandas API want
    that one.
    """
    import narwhals.stable.v2 as nw
    return nw.dependencies.is_into_dataframe(obj)


def to_narwhals(obj: t.Any) -> nw.DataFrame[t.Any]:
    """
    Wrap a native DataFrame in a Narwhals DataFrame.

    The wrapper is a view, so this does not copy the data and
    `to_narwhals(df).to_native()` returns the object that was passed in.

    Parameters
    ----------
    obj: DataFrame
      A DataFrame from any library Narwhals supports.

    Returns
    -------
    The Narwhals DataFrame wrapping obj.

    Raises
    ------
    TypeError: If the object is not a supported DataFrame.
    """
    import narwhals.stable.v2 as nw
    return nw.from_native(obj, eager_only=True)
