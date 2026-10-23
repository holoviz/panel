"""
Tests for table widgets displaying DataFrames without a row index,
e.g. Polars DataFrames and PyArrow Tables, via Narwhals.
"""
import datetime as dt

import numpy as np
import pandas as pd
import param
import pytest

from panel.models.tabulator import CellClickEvent, TableEditEvent
from panel.tests.util import serve_and_request, wait_until
from panel.util.dataframe import (
    ROW_INDEX, has_index, is_dataframe, is_indexless, sort_frame, to_narwhals,
)
from panel.widgets import TextInput
from panel.widgets.tables import DataFrame, Tabulator

pl = pytest.importorskip('polars')
pa = pytest.importorskip('pyarrow')

pytestmark = pytest.mark.filterwarnings(
    "ignore:'DataFrame' is deprecated:panel.util.warnings.PanelDeprecationWarning"
)

DATA = {
    'int': [1, 2, 3],
    'float': [3.14, 6.28, 9.42],
    'str': ['A', 'B', 'C'],
}


def to_polars(data):
    return pl.DataFrame(data)


def to_pyarrow(data):
    return pa.table(data)


@pytest.fixture(params=[to_polars, to_pyarrow], ids=['polars', 'pyarrow'])
def backend(request):
    return request.param


@pytest.fixture
def frame(backend):
    return backend(DATA)


def to_dict(df):
    """Converts a frame of any backend into a dictionary of lists."""
    if has_index(df):
        return df.to_dict('list')
    return to_narwhals(df).to_dict(as_series=False)


def to_pandas(data):
    return pd.DataFrame(data)


def assert_same_frame_type(result, expected):
    assert type(result) is type(expected)


# Helper functions

@pytest.mark.parametrize('obj, expected', [
    (pd.DataFrame(DATA), True),
    (None, False),
    ({'a': [1]}, False),
])
def test_has_index(obj, expected):
    assert has_index(obj) is expected


def test_has_index_indexless(frame):
    assert not has_index(frame)
    assert is_indexless(frame)


@pytest.mark.parametrize('value', [None, 'not tabular', 42, {'a': [1]}, [1, 2, 3]])
def test_is_dataframe_rejects_non_frames(value):
    assert not is_dataframe(value)


def test_is_dataframe(frame):
    assert is_dataframe(frame)
    assert is_dataframe(pd.DataFrame(DATA))


def test_sort_frame_matches_pandas_sort(backend):
    data = {
        'str': ['b', 'A', None, 'a', 'B', 'c', 'a'],
        'float': [1.0, np.nan, 2.0, None, 3.0, 1.0, 2.0],
        'int': [2, 1, 2, 1, 2, 1, 1],
    }
    sorters = [
        [('str', True)], [('str', False)], [('float', True)], [('float', False)],
        [('int', True), ('str', False)], [('int', False), ('float', True)],
    ]
    for spec in sorters:
        fields = [f for f, _ in spec]
        ascending = [a for _, a in spec]
        table = Tabulator(pd.DataFrame(data), sorters=[
            {'field': f, 'dir': 'asc' if a else 'desc'} for f, a in spec
        ])
        expected = table.current_view
        result = to_dict(sort_frame(backend(data), fields, ascending))
        np.testing.assert_equal(result['int'], expected['int'].tolist())
        np.testing.assert_equal(
            [None if v is None else v for v in result['str']],
            [None if pd.isna(v) else v for v in expected['str']]
        )


# Construction and rendering

@pytest.mark.parametrize('widget', [Tabulator, DataFrame])
def test_table_renders(widget, frame, document, comm):
    table = widget(frame)
    model = table.get_root(document, comm)

    assert table.indexes == []
    assert list(model.source.data) == ['int', 'float', 'str']
    np.testing.assert_array_equal(model.source.data['int'], [1, 2, 3])
    np.testing.assert_array_equal(model.source.data['float'], [3.14, 6.28, 9.42])
    np.testing.assert_array_equal(model.source.data['str'], ['A', 'B', 'C'])
    assert [c.field for c in model.columns] == ['int', 'float', 'str']


def test_tabulator_string_columns_are_not_fixed_width(frame, document, comm):
    model = Tabulator(frame).get_root(document, comm)

    # Fixed width unicode arrays would truncate edits patched into the data
    assert model.source.data['str'].dtype == object
    model.source.patch({'str': [(0, 'Longer')]})
    assert model.source.data['str'][0] == 'Longer'


def test_tabulator_column_types(backend, document, comm):
    df = backend({
        'int': [1, 2], 'float': [1.0, 2.0], 'bool': [True, False],
        'str': ['A', 'B'], 'date': [dt.date(2020, 1, 1), dt.date(2020, 1, 2)],
        'datetime': [dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 2)],
    })
    table = Tabulator(df)
    model = table.get_root(document, comm)

    editors = {c.field: c.editor['type'] for c in model.columns}
    formatters = {c.field: c.formatter for c in model.columns}
    assert editors == {
        'int': 'IntEditor', 'float': 'NumberEditor', 'bool': 'CheckboxEditor',
        'str': 'StringEditor', 'date': 'DateEditor', 'datetime': 'DateEditor',
    }
    assert formatters['date']['format'] == '%Y-%m-%d'
    assert formatters['datetime']['format'] == '%Y-%m-%d %H:%M:%S'
    sorters = {c['field']: c.get('sorter') for c in model.configuration['columns']}
    assert sorters == {
        'int': 'number', 'float': 'number', 'bool': 'boolean', 'str': None,
        'date': 'timestamp', 'datetime': 'timestamp',
    }
    # Datetimes are sent as millisecond timestamps
    assert model.source.data['date'].tolist() == [1577836800000.0, 1577923200000.0]
    assert model.source.data['datetime'].tolist() == [1577836800000.0, 1577923200000.0]


def test_tabulator_null_values(backend, document, comm):
    df = backend({'int': [1, None], 'str': ['A', None], 'bool': [True, None]})
    table = Tabulator(df)
    model = table.get_root(document, comm)

    assert model.source.data['str'].tolist() == ['A', None]
    assert list(model.source.data['bool']) == [True, None]
    assert np.isnan(model.source.data['int'][1])


def test_tabulator_show_index_has_no_effect(frame, document, comm):
    table = Tabulator(frame, show_index=False)
    model = table.get_root(document, comm)

    assert table.indexes == []
    assert [c.field for c in model.columns] == ['int', 'float', 'str']
    assert model.hidden_columns == []


def test_tabulator_rejects_row_index_column(backend):
    with pytest.raises(ValueError, match=ROW_INDEX):
        Tabulator(backend({ROW_INDEX: [1, 2]}))


def test_tabulator_replace_value_backend(frame, document, comm):
    table = Tabulator(pd.DataFrame(DATA))
    model = table.get_root(document, comm)

    table.value = frame

    assert [c.field for c in model.columns] == ['int', 'float', 'str']
    np.testing.assert_array_equal(model.source.data['int'], [1, 2, 3])
    assert 'index' not in model.source.data


def test_tabulator_styler_not_applied(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)

    assert model.cell_styles == {}


def test_tabulator_automatic_pagination(backend):
    table = Tabulator(backend({'a': list(range(300))}))

    assert table.pagination == 'local'


# Filtering

def test_tabulator_constant_scalar_filter(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)

    table.add_filter('B', 'str')

    np.testing.assert_array_equal(model.source.data['int'], [2])
    assert table._index_mapping == {0: 1}
    assert_same_frame_type(table.current_view, frame)
    assert to_dict(table.current_view) == {'int': [2], 'float': [6.28], 'str': ['B']}


def test_tabulator_constant_list_filter(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)

    table.add_filter(['A', 'C'], 'str')

    np.testing.assert_array_equal(model.source.data['int'], [1, 3])
    assert table._index_mapping == {0: 0, 1: 2}


@pytest.mark.parametrize('value, expected', [
    ((2, None), [2, 3]), ((None, 2), [1, 2]), ((2, 2), [2]), ((None, None), [1, 2, 3])
])
def test_tabulator_constant_tuple_filter(frame, document, comm, value, expected):
    table = Tabulator(frame)
    model = table.get_root(document, comm)

    table.add_filter(value, 'int')

    np.testing.assert_array_equal(model.source.data['int'], expected)


def test_tabulator_widget_filter(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)
    widget = TextInput(value='A')

    table.add_filter(widget, 'str')
    np.testing.assert_array_equal(model.source.data['int'], [1])

    widget.value = 'C'
    np.testing.assert_array_equal(model.source.data['int'], [3])


def test_tabulator_function_mask_filter(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)

    seen = []
    def filt(df):
        seen.append(type(df))
        return to_narwhals(df)['int'].to_numpy() > 1

    table.add_filter(filt)

    assert seen[-1] is type(frame)
    np.testing.assert_array_equal(model.source.data['int'], [2, 3])
    assert table._index_mapping == {0: 1, 1: 2}


def test_tabulator_function_frame_filter(frame, document, comm):
    import narwhals.stable.v2 as nw

    table = Tabulator(frame)
    model = table.get_root(document, comm)

    table.add_filter(lambda df: to_narwhals(df).filter(nw.col('int') != 2).to_native())

    np.testing.assert_array_equal(model.source.data['int'], [1, 3])
    assert table._index_mapping == {0: 0, 1: 2}


def test_tabulator_combined_filters(frame, document, comm):
    import narwhals.stable.v2 as nw

    table = Tabulator(frame)
    model = table.get_root(document, comm)

    table.add_filter((2, None), 'int')
    table.add_filter(lambda df: to_narwhals(df).filter(nw.col('str') != 'C').to_native())
    table.add_filter(lambda df: to_narwhals(df)['float'].to_numpy() > 0)

    np.testing.assert_array_equal(model.source.data['int'], [2])
    assert table._index_mapping == {0: 1}


def test_tabulator_edited_row_kept_despite_header_filter(frame, document, comm):
    table = Tabulator(
        frame, pagination='remote', filters=[{'field': 'str', 'type': 'like', 'value': 'b'}]
    )
    table.get_root(document, comm)

    table._process_event(TableEditEvent(model=None, column='str', row=0, value='Z', old='B'))
    table._process_events({'data': {'int': [2], 'float': [6.28], 'str': ['Z']}})

    assert table._edited_indexes == [1]
    assert to_dict(table.value)['str'] == ['A', 'Z', 'C']
    assert to_dict(table.current_view)['str'] == ['Z']


def test_tabulator_function_filter_dropping_row_index_errors(frame):
    table = Tabulator(frame)

    with pytest.raises(ValueError, match=ROW_INDEX):
        table.add_filter(lambda df: to_narwhals(df).select('int').to_native())


@pytest.mark.parametrize('filt, expected', [
    ({'field': 'str', 'type': 'like', 'value': 'b'}, [2]),
    ({'field': 'str', 'type': 'starts', 'value': 'c'}, [3]),
    ({'field': 'str', 'type': 'ends', 'value': 'a'}, [1]),
    ({'field': 'str', 'type': 'in', 'value': ['A', 'C']}, [1, 3]),
    ({'field': 'int', 'type': '=', 'value': '2'}, [2]),
    ({'field': 'int', 'type': '!=', 'value': 2}, [1, 3]),
    ({'field': 'float', 'type': '>', 'value': 5}, [2, 3]),
    ({'field': 'float', 'type': '<=', 'value': '6.28'}, [1, 2]),
    ({'field': 'str', 'type': 'keywords', 'value': 'a c'}, [1, 3]),
])
def test_tabulator_header_filters(frame, filt, expected):
    pandas_table = Tabulator(pd.DataFrame(DATA), filters=[filt])
    table = Tabulator(frame, filters=[filt])

    assert to_dict(table.current_view)['int'] == expected
    assert pandas_table.current_view['int'].tolist() == expected


def test_tabulator_header_filters_remote_pagination(frame, document, comm):
    table = Tabulator(
        frame, pagination='remote',
        filters=[{'field': 'str', 'type': 'like', 'value': 'b'}]
    )
    model = table.get_root(document, comm)

    np.testing.assert_array_equal(model.source.data['int'], [2])
    assert to_dict(table.current_view)['int'] == [2]


# Sorting and pagination

@pytest.mark.parametrize('pagination', [None, 'local', 'remote'])
def test_tabulator_sorters(frame, pagination, document, comm):
    table = Tabulator(frame, pagination=pagination, sorters=[{'field': 'int', 'dir': 'desc'}])
    model = table.get_root(document, comm)

    assert_same_frame_type(table.current_view, frame)
    assert to_dict(table.current_view)['int'] == [3, 2, 1]
    if pagination == 'remote':
        np.testing.assert_array_equal(model.source.data['int'], [3, 2, 1])
        assert table._index_mapping == {0: 2, 1: 1, 2: 0}
    else:
        np.testing.assert_array_equal(model.source.data['int'], [1, 2, 3])


def test_tabulator_remote_pagination(backend, document, comm):
    table = Tabulator(backend({'a': list(range(10))}), pagination='remote', page_size=3)
    model = table.get_root(document, comm)

    np.testing.assert_array_equal(model.source.data['a'], [0, 1, 2])
    assert model.max_page == 4

    table.page = 4
    np.testing.assert_array_equal(model.source.data['a'], [9])

    table.sorters = [{'field': 'a', 'dir': 'desc'}]
    table.page = 1
    np.testing.assert_array_equal(model.source.data['a'], [9, 8, 7])


# Selection

def test_tabulator_selected_dataframe(frame):
    table = Tabulator(frame, selection=[0, 2])

    assert_same_frame_type(table.selected_dataframe, frame)
    assert to_dict(table.selected_dataframe)['int'] == [1, 3]


def test_tabulator_selected_dataframe_empty(frame):
    table = Tabulator(frame)

    assert_same_frame_type(table.selected_dataframe, frame)
    assert len(table.selected_dataframe) == 0


def test_tabulator_selection_with_filter(frame, document, comm):
    table = Tabulator(frame, selection=[0, 2])
    model = table.get_root(document, comm)

    table.add_filter([2, 3], 'int')

    assert model.source.selected.indices == [1]


def test_tabulator_selection_remote_pagination(backend, document, comm):
    table = Tabulator(
        backend({'a': list(range(10))}), pagination='remote', page_size=3,
        sorters=[{'field': 'a', 'dir': 'desc'}]
    )
    model = table.get_root(document, comm)

    table._process_events({'indices': [0, 2]})
    assert table.selection == [9, 7]

    table.page = 2
    table.selection = [5, 9]
    assert model.source.selected.indices == [1]


def test_tabulator_selection_event_with_sorters(frame):
    table = Tabulator(frame, pagination='remote', sorters=[{'field': 'int', 'dir': 'desc'}])

    table._process_events({'indices': [0]})

    assert table.selection == [2]
    assert to_dict(table.selected_dataframe)['int'] == [3]


def test_tabulator_selection_resets_on_shorter_value(backend):
    table = Tabulator(backend({'a': [1, 2, 3]}), selection=[0, 2])

    table.value = backend({'a': [1, 2]})

    assert table.selection == [0]


def test_tabulator_selectable_rows(frame, document, comm):
    seen = []
    def selectable(df):
        seen.append(type(df))
        assert ROW_INDEX not in to_narwhals(df).columns
        return [0, 1]

    table = Tabulator(frame, selectable_rows=selectable)
    model = table.get_root(document, comm)

    assert seen[-1] is type(frame)
    assert model.selectable_rows == [0, 1]


# Editing

@pytest.mark.parametrize('pagination', [None, 'remote'])
def test_tabulator_edit(frame, pagination, document, comm):
    table = Tabulator(frame, pagination=pagination)
    table.get_root(document, comm)
    events = []
    table.param.watch(events.append, 'value')

    table._process_events({'data': {'int': [5, 7, 9]}})

    assert_same_frame_type(table.value, frame)
    assert to_dict(table.value) == dict(DATA, int=[5, 7, 9])
    assert to_dict(table.current_view)['int'] == [5, 7, 9]
    assert len(events) == 1
    assert to_dict(events[0].old)['int'] == [1, 2, 3]
    assert events[0].new is table.value


def test_tabulator_edit_does_not_trigger_when_unchanged(frame):
    table = Tabulator(frame)
    events = []
    table.param.watch(events.append, 'value')

    table._process_events({'data': {'int': [1, 2, 3]}})

    assert table.value is frame
    assert events == []


def test_tabulator_edit_with_sorters_remote_pagination(frame, document, comm):
    table = Tabulator(frame, pagination='remote', sorters=[{'field': 'int', 'dir': 'desc'}])
    table.get_root(document, comm)

    table._process_events({'data': {'str': ['c', 'b', 'a']}})

    assert to_dict(table.value)['str'] == ['a', 'b', 'c']
    assert to_dict(table.current_view)['str'] == ['c', 'b', 'a']


def test_tabulator_edit_with_filter(frame, document, comm):
    table = Tabulator(frame)
    table.get_root(document, comm)
    table.add_filter([1, 3], 'int')

    table._process_events({'data': {'float': [0.1, 0.3]}})

    assert to_dict(table.value)['float'] == [0.1, 6.28, 0.3]


def test_tabulator_edit_integer_with_nulls(backend):
    table = Tabulator(backend({'a': [1, None, 3]}))

    table._process_events({'data': {'a': [1, np.nan, 4]}})

    assert to_dict(table.value)['a'] == [1, None, 4]
    assert to_narwhals(table.value).schema['a'] == to_narwhals(backend({'a': [1]})).schema['a']


def test_tabulator_edit_datetime(backend):
    table = Tabulator(backend({'a': [dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 2)]}))

    table._process_events({'data': {'a': [1577836800000.0, 1578009600000.0]}})

    assert to_dict(table.value)['a'] == [dt.datetime(2020, 1, 1), dt.datetime(2020, 1, 3)]


def test_tabulator_edit_event(frame):
    table = Tabulator(frame, sorters=[{'field': 'int', 'dir': 'desc'}], pagination='remote')
    events = []
    table.on_edit(events.append)

    table._process_event(TableEditEvent(model=None, column='str', row=0, value='Z', old='C'))
    assert events == []

    table._process_events({'data': {'str': ['Z', 'B', 'A']}})

    assert len(events) == 1
    assert events[0].row == 2
    assert events[0].value == 'Z'
    assert events[0].old == 'C'
    assert to_dict(table.value)['str'] == ['A', 'B', 'Z']


def test_tabulator_cell_click_event(frame):
    table = Tabulator(frame, sorters=[{'field': 'int', 'dir': 'desc'}], pagination='remote')
    values = []
    table.on_click(lambda e: values.append((e.column, e.row, e.value)))

    table._process_event(CellClickEvent(model=None, column='str', row=0))

    assert values == [('str', 2, 'C')]


def test_server_edit_event(frame):
    table = Tabulator(frame)

    serve_and_request(table)
    wait_until(lambda: bool(table._models))

    ref, (model, _) = list(table._models.items())[0]
    doc = list(table._documents.keys())[0]
    events = []
    table.on_edit(events.append)

    new_data = dict(model.source.data)
    new_data['float'] = np.array([3.14, 1.5, 9.42])

    table._server_event(doc, TableEditEvent(model, 'float', 1, value=1.5, old=6.28))
    wait_until(lambda: bool(table._pending_edits))
    table._server_change(doc, ref, None, 'data', model.source.data, new_data)

    wait_until(lambda: len(events) == 1)
    assert events[0].value == 1.5
    assert to_dict(table.value)['float'] == [3.14, 1.5, 9.42]


def test_dataframe_widget_edit(frame):
    table = DataFrame(frame)

    table._process_events({'data': {'str': ['C', 'B', 'A']}})

    assert to_dict(table.value)['str'] == ['C', 'B', 'A']


# Streaming and patching

@pytest.mark.parametrize('stream', [
    lambda b: {'int': [4], 'float': [12.56], 'str': ['D']},
    lambda b: {'int': 4, 'float': 12.56, 'str': 'D'},
    lambda b: b({'int': [4], 'float': [12.56], 'str': ['D']}),
    lambda b: pd.DataFrame({'int': [4], 'float': [12.56], 'str': ['D']}, index=[10]),
    lambda b: pd.Series({'int': 4, 'float': 12.56, 'str': 'D'}),
], ids=['dict-columns', 'dict-row', 'frame', 'pandas', 'series'])
def test_tabulator_stream(backend, stream, document, comm):
    frame = backend(DATA)
    table = Tabulator(frame)
    model = table.get_root(document, comm)
    events = []
    table.param.watch(events.append, 'value')

    table.stream(stream(backend))

    assert_same_frame_type(table.value, frame)
    assert to_dict(table.value) == {
        'int': [1, 2, 3, 4], 'float': [3.14, 6.28, 9.42, 12.56], 'str': ['A', 'B', 'C', 'D']
    }
    np.testing.assert_array_equal(model.source.data['int'], [1, 2, 3, 4])
    assert len(events) == 1


def test_tabulator_stream_rollover(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)

    table.stream({'int': [4, 5], 'float': [0.0, 0.0], 'str': ['D', 'E']}, rollover=3)

    assert to_dict(table.value)['int'] == [3, 4, 5]
    np.testing.assert_array_equal(model.source.data['int'], [3, 4, 5])
    assert table._index_mapping == {0: 0, 1: 1, 2: 2}


def test_tabulator_stream_missing_columns(frame):
    table = Tabulator(frame)

    table.stream({'int': [4]})

    assert to_dict(table.value) == {
        'int': [1, 2, 3, 4], 'float': [3.14, 6.28, 9.42, None], 'str': ['A', 'B', 'C', None]
    }


def test_tabulator_stream_lossy_cast_raises(backend, frame):
    table = Tabulator(frame)

    with pytest.raises(ValueError, match="Cannot cast column 'int' from Float64 to Int64"):
        table.stream(backend({'int': [4.5], 'float': [0.0], 'str': ['D']}))

    assert to_dict(table.value) == DATA


def test_tabulator_stream_lossless_cast(backend, frame):
    table = Tabulator(frame)

    table.stream(backend({'int': [4.0], 'float': [1], 'str': ['D']}))

    assert to_dict(table.value)['int'] == [1, 2, 3, 4]
    assert to_dict(table.value)['float'] == [3.14, 6.28, 9.42, 1.0]


def test_tabulator_stream_with_filter(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)
    table.add_filter((2, None), 'int')

    table.stream({'int': [0, 4], 'float': [0.0, 0.0], 'str': ['D', 'E']})

    np.testing.assert_array_equal(model.source.data['int'], [2, 3, 4])
    assert table._index_mapping == {0: 1, 1: 2, 2: 4}


def test_tabulator_stream_remote_pagination_follow(backend, document, comm):
    table = Tabulator(backend({'a': list(range(10))}), pagination='remote', page_size=3)
    model = table.get_root(document, comm)

    table.stream({'a': [10, 11, 12]})

    assert table.page == 5
    np.testing.assert_array_equal(model.source.data['a'], [12])


def test_tabulator_patch(frame, document, comm):
    table = Tabulator(frame)
    model = table.get_root(document, comm)

    table.patch({'int': [(0, 10), (slice(1, 3), [20, 30])], 'str': [(2, 'Z')]})

    assert_same_frame_type(table.value, frame)
    assert to_dict(table.value) == dict(DATA, int=[10, 20, 30], str=['A', 'B', 'Z'])
    np.testing.assert_array_equal(model.source.data['int'], [10, 20, 30])
    np.testing.assert_array_equal(model.source.data['str'], ['A', 'B', 'Z'])


def test_tabulator_patch_with_sorters(frame, document, comm):
    table = Tabulator(frame, sorters=[{'field': 'int', 'dir': 'desc'}])
    model = table.get_root(document, comm)

    table.patch({'int': [(0, 10)]})

    assert to_dict(table.value)['int'] == [10, 2, 3]
    np.testing.assert_array_equal(model.source.data['int'], [10, 2, 3])
    assert to_dict(table.current_view)['int'] == [10, 3, 2]


def test_tabulator_patch_with_datetime(backend, document, comm):
    table = Tabulator(backend({'a': [dt.datetime(2020, 1, 1)]}))
    model = table.get_root(document, comm)

    table.patch({'a': [(0, dt.datetime(2020, 1, 2))]})

    assert to_dict(table.value)['a'] == [dt.datetime(2020, 1, 2)]
    assert model.source.data['a'].tolist() == [1577923200000.0]


def test_tabulator_patch_with_frame_errors(frame):
    table = Tabulator(frame)

    with pytest.raises(ValueError, match='Patching a'):
        table.patch(pd.DataFrame({'int': [1]}))


# Row content

@pytest.mark.parametrize('embed_content', [True, False])
def test_tabulator_row_content(frame, embed_content, document, comm):
    rows = []
    def content(row):
        rows.append(row)
        return row['str']

    table = Tabulator(
        frame, row_content=content, embed_content=embed_content,
        sorters=[{'field': 'int', 'dir': 'desc'}], pagination='remote'
    )
    model = table.get_root(document, comm)

    if embed_content:
        assert len(model.children) == 3
        assert rows[0] == {'int': 3, 'float': 9.42, 'str': 'C'}
    else:
        assert len(model.children) == 0

    table._process_events({'expanded': [0]})

    assert table.expanded == [2]
    assert model.expanded == [0]
    assert model.children[0].text == '&lt;p&gt;C&lt;/p&gt;\n'


# Param integration

def test_tabulator_from_param(backend):
    class Obj(param.Parameterized):
        data = param.Parameter()

    obj = Obj(data=backend(DATA))
    table = Tabulator.from_param(obj.param.data)

    table._process_events({'data': {'int': [5, 7, 9]}})

    assert to_dict(obj.data)['int'] == [5, 7, 9]
