"""
Support matrix for non-pandas DataFrame backends.

Panel depends on narwhals and Bokeh already accepts any narwhals compatible
frame as ColumnDataSource input, but Panel's own tabular components are still
pandas only. The entry point tests below record which combinations do not work
yet as strict xfails, so a change that fixes one of them fails loudly instead
of passing silently.
"""
import datetime as dt

import pandas as pd
import pytest

from bokeh.document import Document

from panel.pane import DataFrame as DataFramePane, Perspective
from panel.util.dataframe import is_dataframe, to_narwhals
from panel.widgets import DataFrame as DataFrameWidget, Tabulator

DATA = {'a': [1, 2, 3], 'b': ['x', 'y', 'z']}
FILTER_DATA = {'n': [1, 2, 3], 'w': ['alpha', 'beta', 'gamma']}
TYPED_DATA = {
    'i': [1, 2],
    'f': [1.5, 2.5],
    'b': [True, False],
    's': ['x', 'y'],
    'd': [dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 2)],
}


def pandas_frame(data=DATA):
    return pd.DataFrame(data)


def polars_frame(data=DATA):
    pl = pytest.importorskip('polars')
    return pl.DataFrame(data)


def pyarrow_frame(data=DATA):
    pa = pytest.importorskip('pyarrow')
    return pa.table(data)


BACKENDS = [pandas_frame, polars_frame, pyarrow_frame]
BACKEND_IDS = ['pandas', 'polars', 'pyarrow']

_unsupported = pytest.mark.xfail(strict=True, reason='backend not supported yet')
ENTRY_POINT_BACKENDS = [
    pytest.param(pandas_frame, id='pandas'),
    pytest.param(polars_frame, id='polars', marks=_unsupported),
    pytest.param(pyarrow_frame, id='pyarrow', marks=_unsupported),
]
# Tables read any backend; the panes do not yet.
TABLE_BACKENDS = [pytest.param(f, id=i) for f, i in zip(BACKENDS, BACKEND_IDS, strict=True)]


@pytest.mark.parametrize('frame', BACKENDS, ids=BACKEND_IDS)
def test_has_index_is_true_only_for_pandas_like_frames(frame):
    from panel.util.dataframe import has_index

    assert has_index(frame()) is (frame is pandas_frame)


@pytest.mark.parametrize('frame', BACKENDS, ids=BACKEND_IDS)
def test_is_dataframe_accepts_every_backend(frame):
    assert is_dataframe(frame())


@pytest.mark.parametrize('value', [None, 'not tabular', 42, {'a': [1]}, [1, 2, 3]])
def test_is_dataframe_rejects_non_frames(value):
    assert not is_dataframe(value)


@pytest.mark.parametrize('frame', BACKENDS, ids=BACKEND_IDS)
def test_to_narwhals_round_trips_to_the_original_object(frame):
    native = frame()

    assert to_narwhals(native).to_native() is native


@pytest.mark.parametrize('frame', BACKENDS, ids=BACKEND_IDS)
def test_to_narwhals_exposes_columns_uniformly(frame):
    assert to_narwhals(frame()).columns == ['a', 'b']


def test_to_narwhals_rejects_non_frames():
    with pytest.raises(TypeError):
        to_narwhals('not tabular')


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_tabulator_accepts_frame(frame):
    assert Tabulator(frame()) is not None


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_tabulator_renders_frame(frame):
    table = Tabulator(frame())

    table.server_doc(doc=Document(), title='t')

    assert set(table._data) >= {'a', 'b'}


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_tabulator_picks_editors_from_column_types(frame):
    from bokeh.models.widgets.tables import (
        CheckboxEditor, DateEditor, IntEditor, NumberEditor, StringEditor,
    )

    table = Tabulator(frame(TYPED_DATA))
    columns = {c.field: c for c in table._get_columns()}

    assert isinstance(columns['i'].editor, IntEditor)
    assert isinstance(columns['f'].editor, NumberEditor)
    assert isinstance(columns['b'].editor, CheckboxEditor)
    assert isinstance(columns['s'].editor, StringEditor)
    assert isinstance(columns['d'].editor, DateEditor)


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_tabulator_indexes_are_empty_for_index_less_backends(frame):
    table = Tabulator(frame())

    assert table.indexes == (['index'] if frame is pandas_frame else [])


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_dataframe_widget_accepts_frame(frame):
    assert DataFrameWidget(frame()) is not None


@pytest.mark.parametrize('frame', ENTRY_POINT_BACKENDS)
def test_dataframe_pane_accepts_frame(frame):
    assert DataFramePane(frame()) is not None


@pytest.mark.parametrize('frame', ENTRY_POINT_BACKENDS)
def test_perspective_accepts_frame(frame):
    assert Perspective(frame()) is not None


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
@pytest.mark.parametrize(('op', 'value', 'expected'), [
    ('=', 2, [2]),
    ('!=', 2, [1, 3]),
    ('<', 3, [1, 2]),
    ('>=', 2, [2, 3]),
    ('in', [1, 3], [1, 3]),
])
def test_header_filters_apply_on_any_backend(frame, op, value, expected):
    table = Tabulator(frame(FILTER_DATA), header_filters=True)

    table.filters = [{'field': 'n', 'type': op, 'value': value}]

    assert list(to_narwhals(table.current_view)['n']) == expected


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
@pytest.mark.parametrize(('op', 'value', 'expected'), [
    ('like', 'ph', ['alpha']),
    ('starts', 'be', ['beta']),
    ('ends', 'MA', ['gamma']),
])
def test_string_header_filters_apply_on_any_backend(frame, op, value, expected):
    table = Tabulator(frame(FILTER_DATA), header_filters=True)

    table.filters = [{'field': 'w', 'type': op, 'value': value}]

    assert list(to_narwhals(table.current_view)['w']) == expected


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_constant_filters_apply_on_any_backend(frame):
    table = Tabulator(frame(FILTER_DATA))

    table.add_filter(2, 'n')

    assert list(to_narwhals(table.current_view)['n']) == [2]


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_range_filters_apply_on_any_backend(frame):
    table = Tabulator(frame(FILTER_DATA))

    table.add_filter((2, 3), 'n')

    assert list(to_narwhals(table.current_view)['n']) == [2, 3]


@pytest.mark.parametrize('frame', TABLE_BACKENDS)
def test_filter_callables_receive_their_own_backend(frame):
    seen = []
    native = frame(FILTER_DATA)
    table = Tabulator(native)

    table.add_filter(lambda df: seen.append(type(df)) or df)
    view = table.current_view

    assert seen == [type(native)]
    assert len(view) == 3


def test_filter_callables_receive_the_native_frame():
    """
    add_filter() hands the frame to user code, which expects a concrete object
    from its own backend. Narwhals wrappers must never leak out here.
    """
    seen = []
    table = Tabulator(pandas_frame())
    table.add_filter(lambda df: seen.append(type(df)) or df)

    view = table.current_view

    assert seen == [pd.DataFrame]
    assert len(view) == 3
