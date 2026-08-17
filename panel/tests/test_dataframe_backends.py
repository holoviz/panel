"""
Support matrix for non-pandas DataFrame backends.

Panel depends on narwhals and Bokeh already accepts any narwhals compatible
frame as ColumnDataSource input, but Panel's own tabular components are still
pandas only. The entry point tests below record which combinations do not work
yet as strict xfails, so a change that fixes one of them fails loudly instead
of passing silently.
"""
import pandas as pd
import pytest

from panel._dataframe import is_dataframe, to_narwhals
from panel.pane import DataFrame as DataFramePane, Perspective
from panel.widgets import DataFrame as DataFrameWidget, Tabulator

DATA = {'a': [1, 2, 3], 'b': ['x', 'y', 'z']}


def pandas_frame():
    return pd.DataFrame(DATA)


def polars_frame():
    pl = pytest.importorskip('polars')
    return pl.DataFrame(DATA)


def pyarrow_frame():
    pa = pytest.importorskip('pyarrow')
    return pa.table(DATA)


BACKENDS = [pandas_frame, polars_frame, pyarrow_frame]
BACKEND_IDS = ['pandas', 'polars', 'pyarrow']

_unsupported = pytest.mark.xfail(strict=True, reason='backend not supported yet')
ENTRY_POINT_BACKENDS = [
    pytest.param(pandas_frame, id='pandas'),
    pytest.param(polars_frame, id='polars', marks=_unsupported),
    pytest.param(pyarrow_frame, id='pyarrow', marks=_unsupported),
]


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


@pytest.mark.parametrize('frame', ENTRY_POINT_BACKENDS)
def test_tabulator_accepts_frame(frame):
    assert Tabulator(frame()) is not None


@pytest.mark.parametrize('frame', ENTRY_POINT_BACKENDS)
def test_dataframe_widget_accepts_frame(frame):
    assert DataFrameWidget(frame()) is not None


@pytest.mark.parametrize('frame', ENTRY_POINT_BACKENDS)
def test_dataframe_pane_accepts_frame(frame):
    assert DataFramePane(frame()) is not None


@pytest.mark.parametrize('frame', ENTRY_POINT_BACKENDS)
def test_perspective_accepts_frame(frame):
    assert Perspective(frame()) is not None


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
