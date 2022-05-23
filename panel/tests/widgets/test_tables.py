import datetime as dt
import time

from packaging.version import Version

import numpy as np
import pytest
import requests

try:
    import pandas as pd
    from pandas._testing import (
        makeCustomDataframe, makeMixedDataFrame, makeTimeDataFrame
    )
except ImportError:
    pytestmark = pytest.mark.skip('pandas not available')

from bokeh.models.widgets.tables import (
    NumberFormatter, IntEditor, NumberEditor, StringFormatter,
    SelectEditor, DateFormatter, DataCube, CellEditor,
    SumAggregator, AvgAggregator, MinAggregator
)

from panel.depends import bind
from panel.io.server import serve
from panel.io.state import set_curdoc
from panel.models.tabulator import CellClickEvent, TableEditEvent
from panel.widgets import Button, TextInput
from panel.widgets.tables import DataFrame, Tabulator

pd_old = pytest.mark.skipif(Version(pd.__version__) < Version('1.3'),
                            reason="Requires latest pandas")


def test_dataframe_widget(dataframe, document, comm):

    table = DataFrame(dataframe)

    model = table.get_root(document, comm)

    index_col, int_col, float_col, str_col = model.columns

    assert index_col.title == 'index'
    assert isinstance(index_col.formatter, NumberFormatter)
    assert isinstance(index_col.editor, CellEditor)

    assert int_col.title == 'int'
    assert isinstance(int_col.formatter, NumberFormatter)
    assert isinstance(int_col.editor, IntEditor)

    assert float_col.title == 'float'
    assert isinstance(float_col.formatter, NumberFormatter)
    assert isinstance(float_col.editor, NumberEditor)

    assert str_col.title == 'str'
    assert isinstance(float_col.formatter, StringFormatter)
    assert isinstance(float_col.editor, NumberEditor)


def test_dataframe_widget_no_show_index(dataframe, document, comm):
    table = DataFrame(dataframe, show_index=False)

    model = table.get_root(document, comm)

    assert len(model.columns) == 3
    int_col, float_col, str_col = model.columns
    assert int_col.title == 'int'
    assert float_col.title == 'float'
    assert str_col.title == 'str'

    table.show_index = True

    assert len(model.columns) == 4
    index_col, int_col, float_col, str_col = model.columns
    assert index_col.title == 'index'
    assert int_col.title == 'int'
    assert float_col.title == 'float'
    assert str_col.title == 'str'


def test_dataframe_widget_datetimes(document, comm):

    table = DataFrame(makeTimeDataFrame())

    model = table.get_root(document, comm)

    dt_col, _, _, _, _ = model.columns

    assert dt_col.title == 'index'
    assert isinstance(dt_col.formatter, DateFormatter)
    assert isinstance(dt_col.editor, CellEditor)


def test_dataframe_editors(dataframe, document, comm):
    editor = SelectEditor(options=['A', 'B', 'C'])
    table = DataFrame(dataframe, editors={'str': editor})
    model = table.get_root(document, comm)

    model_editor = model.columns[-1].editor
    assert isinstance(model_editor, SelectEditor) is not editor
    assert isinstance(model_editor, SelectEditor)
    assert model_editor.options == ['A', 'B', 'C']


def test_dataframe_formatter(dataframe, document, comm):
    formatter = NumberFormatter(format='0.0000')
    table = DataFrame(dataframe, formatters={'float': formatter})
    model = table.get_root(document, comm)
    model_formatter = model.columns[2].formatter
    assert model_formatter is not formatter
    assert isinstance(model_formatter, NumberFormatter)
    assert model_formatter.format == formatter.format


def test_dataframe_triggers(dataframe):
    events = []

    def increment(event, events=events):
        events.append(event)

    table = DataFrame(dataframe)
    table.param.watch(increment, 'value')
    table._process_events({'data': {'str': ['C', 'B', 'A']}})
    assert len(events) == 1


def test_dataframe_does_not_trigger(dataframe):
    events = []

    def increment(event, events=events):
        events.append(event)

    table = DataFrame(dataframe)
    table.param.watch(increment, 'value')
    table._process_events({'data': {'str': ['A', 'B', 'C']}})
    assert len(events) == 0


def test_dataframe_selected_dataframe(dataframe):
    table = DataFrame(dataframe, selection=[0, 2])
    pd.testing.assert_frame_equal(table.selected_dataframe, dataframe.iloc[[0, 2]])


def test_dataframe_process_selection_event(dataframe):
    table = DataFrame(dataframe, selection=[0, 2])
    table._process_events({'indices': [0, 2]})
    pd.testing.assert_frame_equal(table.selected_dataframe, dataframe.iloc[[0, 2]])


def test_dataframe_process_data_event(dataframe):
    df = dataframe.copy()

    table = DataFrame(dataframe, selection=[0, 2])
    table._process_events({'data': {'int': [5, 7, 9]}})
    df['int'] = [5, 7, 9]
    pd.testing.assert_frame_equal(table.value, df)

    table._process_events({'data': {'int': {1: 3, 2: 4, 0: 1}}})
    df['int'] = [1, 3, 4]
    pd.testing.assert_frame_equal(table.value, df)


def test_dataframe_duplicate_column_name(document, comm):
    df = pd.DataFrame([[1, 1], [2, 2]], columns=['col', 'col'])
    with pytest.raises(ValueError):
        table = DataFrame(df)

    df = pd.DataFrame([[1, 1], [2, 2]], columns=['a', 'b'])
    table = DataFrame(df)
    with pytest.raises(ValueError):
        table.value = table.value.rename(columns={'a': 'b'})

    df = pd.DataFrame([[1, 1], [2, 2]], columns=['a', 'b'])
    table = DataFrame(df)
    table.get_root(document, comm)
    with pytest.raises(ValueError):
        table.value = table.value.rename(columns={'a': 'b'})


def test_hierarchical_index(document, comm):
    df = pd.DataFrame([
        ('Germany', 2020, 9, 2.4, 'A'),
        ('Germany', 2021, 3, 7.3, 'C'),
        ('Germany', 2022, 6, 3.1, 'B'),
        ('UK', 2020, 5, 8.0, 'A'),
        ('UK', 2021, 1, 3.9, 'B'),
        ('UK', 2022, 9, 2.2, 'A')
    ], columns=['Country', 'Year', 'Int', 'Float', 'Str']).set_index(['Country', 'Year'])

    table = DataFrame(value=df, hierarchical=True,
                      aggregators={'Year': {'Int': 'sum', 'Float': 'mean'}})

    model = table.get_root(document, comm)
    assert isinstance(model, DataCube)
    assert len(model.grouping) == 1
    grouping = model.grouping[0]
    assert len(grouping.aggregators) == 2
    agg1, agg2 = grouping.aggregators
    assert agg1.field_ == 'Int'
    assert isinstance(agg1, SumAggregator)
    assert agg2.field_ == 'Float'
    assert isinstance(agg2, AvgAggregator)

    table.aggregators = {'Year': 'min'}

    agg1, agg2 = grouping.aggregators
    assert agg1.field_ == 'Int'
    assert isinstance(agg1, MinAggregator)
    assert agg2.field_ == 'Float'
    assert isinstance(agg2, MinAggregator)


def test_table_index_column(document, comm):
    df = pd.DataFrame({
        'int': [1, 2, 3],
        'float': [3.14, 6.28, 9.42],
        'index': ['A', 'B', 'C'],
    }, index=[1, 2, 3])
    table = DataFrame(value=df)

    model = table.get_root(document, comm=comm)

    assert np.array_equal(model.source.data['level_0'], np.array([1, 2, 3]))
    assert model.columns[0].field == 'level_0'
    assert model.columns[0].title == ''


def test_none_table(document, comm):
    table = DataFrame(value=None)
    assert table.indexes == []

    model = table.get_root(document, comm)

    assert model.source.data == {}


def test_tabulator_selected_dataframe():
    df = makeMixedDataFrame()
    table = Tabulator(df, selection=[0, 2])

    pd.testing.assert_frame_equal(table.selected_dataframe, df.iloc[[0, 2]])


def test_tabulator_multi_index(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']))

    model = table.get_root()

    assert model.configuration['columns'] == [
        {'field': 'A'},
        {'field': 'C'},
        {'field': 'B'},
        {'field': 'D'}
    ]

    assert np.array_equal(model.source.data['A'], np.array([0., 1., 2., 3., 4.]))
    assert np.array_equal(model.source.data['C'], np.array(['foo1', 'foo2', 'foo3', 'foo4', 'foo5']))


def test_tabulator_multi_index_remote_pagination(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']), pagination='remote', page_size=3)

    model = table.get_root()

    assert model.configuration['columns'] == [
        {'field': 'A'},
        {'field': 'C'},
        {'field': 'B'},
        {'field': 'D'}
    ]

    assert np.array_equal(model.source.data['A'], np.array([0., 1., 2.]))
    assert np.array_equal(model.source.data['C'], np.array(['foo1', 'foo2', 'foo3']))


def test_tabulator_expanded_content():
    df = makeMixedDataFrame()

    table = Tabulator(df, expanded=[0, 1], row_content=lambda r: r.A)

    model = table.get_root()

    assert len(model.children) == 2

    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;0.0&lt;/pre&gt;"

    assert 1 in model.children
    row1 = model.children[1]
    assert row1.text == "&lt;pre&gt;1.0&lt;/pre&gt;"

    table.expanded = [1, 2]

    assert 0 not in model.children

    assert 1 in model.children
    assert row1 is model.children[1]

    assert 2 in model.children
    row2 = model.children[2]
    assert row2.text == "&lt;pre&gt;2.0&lt;/pre&gt;"


def test_tabulator_index_column(document, comm):
    df = pd.DataFrame({
        'int': [1, 2, 3],
        'float': [3.14, 6.28, 9.42],
        'index': ['A', 'B', 'C'],
    }, index=[1, 2, 3])
    table = Tabulator(value=df)

    model = table.get_root(document, comm=comm)

    assert np.array_equal(model.source.data['level_0'], np.array([1, 2, 3]))
    assert model.columns[0].field == 'level_0'
    assert model.columns[0].title == ''


def test_tabulator_expanded_content_pagination():
    df = makeMixedDataFrame()

    table = Tabulator(df, expanded=[0, 1], row_content=lambda r: r.A, pagination='remote', page_size=2)

    model = table.get_root()

    assert len(model.children) == 2

    table.page = 2

    assert len(model.children) == 0


def test_tabulator_expanded_content_embed():
    df = makeMixedDataFrame()

    table = Tabulator(df, embed_content=True, row_content=lambda r: r.A)

    model = table.get_root()

    assert len(model.children) == len(df)

    for i, r in df.iterrows():
        assert i in model.children
        row = model.children[i]
        assert row.text  == f"&lt;pre&gt;{r.A}&lt;/pre&gt;"

    table.row_content = lambda r: r.A + 1

    for i, r in df.iterrows():
        assert i in model.children
        row = model.children[i]
        assert row.text  == f"&lt;pre&gt;{r.A+1}&lt;/pre&gt;"


def test_tabulator_selected_and_filtered_dataframe(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, selection=list(range(len(df))))

    pd.testing.assert_frame_equal(table.selected_dataframe, df)

    table.add_filter('foo3', 'C')

    pd.testing.assert_frame_equal(table.selected_dataframe, df[df["C"] == "foo3"])

    table.remove_filter('foo3')

    table.selection = [0, 1, 2]

    table.add_filter('foo3', 'C')

    assert table.selection == [0]


def test_tabulator_config_defaults(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index'},
        {'field': 'A'},
        {'field': 'B'},
        {'field': 'C'},
        {'field': 'D'}
    ]
    assert model.configuration['selectable'] == True

def test_tabulator_config_widths_percent(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, widths={'A': '22%', 'B': 100})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index'},
        {'field': 'A', 'width': '22%'},
        {'field': 'B'},
        {'field': 'C'},
        {'field': 'D'}
    ]
    assert model.columns[2].width == 100

def test_tabulator_header_filters_config_boolean(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters=True)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'headerFilter': 'number'},
        {'field': 'A', 'headerFilter': True},
        {'field': 'B', 'headerFilter': True},
        {'field': 'C', 'headerFilter': True},
        {'field': 'D', 'headerFilter': True}
    ]

def test_tabulator_header_filters_column_config_select(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters={'C': 'select'})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index'},
        {'field': 'A'},
        {'field': 'B'},
        {'field': 'C', 'headerFilter': 'select', 'headerFilterParams': {'values': True}},
        {'field': 'D'}
    ]
    assert model.configuration['selectable'] == True

def test_tabulator_header_filters_column_config_dict(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters={
        'C': {'type': 'select', 'values': True, 'func': '!=', 'placeholder': 'Not equal'}
    })

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index'},
        {'field': 'A'},
        {'field': 'B'},
        {
            'field': 'C',
            'headerFilter': 'select',
            'headerFilterParams': {'values': True},
            'headerFilterFunc': '!=',
            'headerFilterPlaceholder': 'Not equal'
        },
        {'field': 'D'}
    ]
    assert model.configuration['selectable'] == True

def test_tabulator_config_formatter_string(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, formatters={'B': 'tickCross'})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'formatter': 'tickCross'}


def test_tabulator_config_formatter_dict(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, formatters={'B': {'type': 'tickCross', 'tristate': True}})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'formatter': 'tickCross', 'formatterParams': {'tristate': True}}


def test_tabulator_config_editor_string(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, editors={'B': 'select'})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'editor': 'select'}


def test_tabulator_config_editor_dict(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, editors={'B': {'type': 'select', 'values': True}})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'editor': 'select', 'editorParams': {'values': True}}


def test_tabulator_groups(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, groups={'Number': ['A', 'B'], 'Other': ['C', 'D']})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index'},
        {'title': 'Number',
         'columns': [
            {'field': 'A'},
            {'field': 'B'}
        ]},
        {'title': 'Other',
         'columns': [
            {'field': 'C'},
            {'field': 'D'}
        ]}
    ]


def test_tabulator_numeric_groups(document, comm):
    df = pd.DataFrame(np.random.rand(10, 3))
    table = Tabulator(df, groups={'Number': [0, 1]})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index'},
        {'title': 'Number',
         'columns': [
            {'field': '0'},
            {'field': '1'}
        ]},
        {'field': '2'}
    ]


def test_tabulator_frozen_cols(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, frozen_columns=['index'])

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'frozen': True},
        {'field': 'A'},
        {'field': 'B'},
        {'field': 'C'},
        {'field': 'D'}
    ]


def test_tabulator_frozen_rows(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, frozen_rows=[0, -1])

    model = table.get_root(document, comm)

    assert model.frozen_rows == [0, 4]

    table.frozen_rows = [1, -2]

    assert model.frozen_rows == [1, 3]


def test_tabulator_selectable_rows(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, selectable_rows=lambda df: list(df[df.A>2].index.values))

    model = table.get_root(document, comm)

    assert model.selectable_rows == [3, 4]


def test_tabulator_pagination(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote', page_size=2)

    model = table.get_root(document, comm)

    assert model.max_page == 3
    assert model.page_size == 2
    assert model.page == 1

    expected = {
        'index': np.array([0, 1]),
        'A': np.array([0, 1]),
        'B': np.array([0, 1]),
        'C': np.array(['foo1', 'foo2']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

    table.page = 2

    expected = {
        'index': np.array([2, 3]),
        'A': np.array([2, 3]),
        'B': np.array([0., 1.]),
        'C': np.array(['foo3', 'foo4']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

    table.page_size = 3
    table.page = 1

    assert model.max_page == 2

    expected = {
        'index': np.array([0, 1, 2]),
        'A': np.array([0, 1, 2]),
        'B': np.array([0, 1, 0]),
        'C': np.array(['foo1', 'foo2', 'foo3']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_pagination_selection(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote', page_size=2)

    model = table.get_root(document, comm)

    table.selection = [2, 3]

    assert model.source.selected.indices == []

    table.page = 2

    assert model.source.selected.indices == [0, 1]

def test_tabulator_pagination_selectable_rows(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(
        df, pagination='remote', page_size=3,
        selectable_rows=lambda df: list(df.index.values[::2])
    )

    model = table.get_root(document, comm)

    assert model.selectable_rows == [0, 2]

    table.page = 2

    assert model.selectable_rows == [3]

@pd_old
def test_tabulator_styling(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    def high_red(value):
        return 'color: red' if value > 2 else 'color: black'

    table.style.applymap(high_red, subset=['A'])

    model = table.get_root(document, comm)

    assert model.styles['data'] == {
        0: {2: [('color', 'black')]},
        1: {2: [('color', 'black')]},
        2: {2: [('color', 'black')]},
        3: {2: [('color', 'red')]},
        4: {2: [('color', 'red')]}
    }

def test_tabulator_empty_table(document, comm):
    value_df = makeMixedDataFrame()
    empty_df = pd.DataFrame([], columns=value_df.columns)
    table = Tabulator(empty_df)

    table.get_root(document, comm)

    assert table.value.shape == empty_df.shape

    table.stream(value_df, follow=True)

    assert table.value.shape == value_df.shape


def test_tabulator_sorters_unnamed_index(document, comm):
    df = pd.DataFrame(np.random.rand(10, 4))
    table = Tabulator(df)

    table.sorters = [{'field': 'index', 'dir': 'desc'}]

    pd.testing.assert_frame_equal(
        table.current_view,
        df.sort_index(ascending=False)
    )

def test_tabulator_sorters_int_name_column(document, comm):
    df = pd.DataFrame(np.random.rand(10, 4))
    table = Tabulator(df)

    table.sorters = [{'field': '0', 'dir': 'desc'}]

    pd.testing.assert_frame_equal(
        table.current_view,
        df.sort_values([0], ascending=False)
    )


def test_tabulator_stream_series(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    stream_value = pd.Series({'A': 5, 'B': 1, 'C': 'foo6', 'D': dt.datetime(2009, 1, 8)})

    table.stream(stream_value)

    assert len(table.value) == 6

    expected = {
        'index': np.array([0, 1, 2, 3, 4, 5]),
        'A': np.array([0, 1, 2, 3, 4, 5]),
        'B': np.array([0, 1, 0, 1, 0, 1]),
        'C': np.array(['foo1', 'foo2', 'foo3', 'foo4', 'foo5', 'foo6']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000',
                       '2009-01-08T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_stream_series_rollover(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    stream_value = pd.Series({'A': 5, 'B': 1, 'C': 'foo6', 'D': dt.datetime(2009, 1, 8)})

    table.stream(stream_value, rollover=5)

    assert len(table.value) == 5

    expected = {
        'index': np.array([1, 2, 3, 4, 5]),
        'A': np.array([1, 2, 3, 4, 5]),
        'B': np.array([1, 0, 1, 0, 1]),
        'C': np.array(['foo2', 'foo3', 'foo4', 'foo5', 'foo6']),
        'D': np.array(['2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000',
                       '2009-01-08T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_stream_df_rollover(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    stream_value = pd.Series({'A': 5, 'B': 1, 'C': 'foo6', 'D': dt.datetime(2009, 1, 8)}).to_frame().T

    table.stream(stream_value, rollover=5)

    assert len(table.value) == 5

    expected = {
        'index': np.array([1, 2, 3, 4, 5]),
        'A': np.array([1, 2, 3, 4, 5]),
        'B': np.array([1, 0, 1, 0, 1]),
        'C': np.array(['foo2', 'foo3', 'foo4', 'foo5', 'foo6']),
        'D': np.array(['2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000',
                       '2009-01-08T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_stream_dict_rollover(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    stream_value = {'A': [5], 'B': [1], 'C': ['foo6'], 'D': [dt.datetime(2009, 1, 8)]}

    table.stream(stream_value, rollover=5)

    assert len(table.value) == 5

    expected = {
        'index': np.array([1, 2, 3, 4, 5]),
        'A': np.array([1, 2, 3, 4, 5]),
        'B': np.array([1, 0, 1, 0, 1]),
        'C': np.array(['foo2', 'foo3', 'foo4', 'foo5', 'foo6']),
        'D': np.array(['2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000',
                       '2009-01-08T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_patch_scalars(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch({'A': [(0, 2), (4, 1)], 'C': [(0, 'foo0')]})

    expected = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([2, 1, 2, 3, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo0', 'foo2', 'foo3', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    for col, values in model.source.data.items():
        if col == 'D':
            expected_array = expected[col].astype(np.int64) / 10e5
        else:
            expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_dataframe(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch(pd.DataFrame({'A': [2, 1]}, index=[0, 4]))

    expected = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([2, 1, 2, 3, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo1', 'foo2', 'foo3', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    for col, values in model.source.data.items():
        if col == 'D':
            expected_array = expected[col].astype(np.int64) / 10e5
        else:
            expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_dataframe_not_as_index(document, comm):
    df = makeMixedDataFrame().sort_values('A', ascending=False)
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch(pd.DataFrame({'A': [2, 1]}, index=[0, 4]), as_index=False)

    expected = {
        'index': np.array([4, 3, 2, 1, 0]),
        'A': np.array([2, 3, 2, 1, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo5', 'foo4', 'foo3', 'foo2', 'foo1']),
        'D': np.array(['2009-01-07T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-01T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    for col, values in model.source.data.items():
        if col == 'D':
            expected_array = expected[col].astype(np.int64) / 10e5
        else:
            expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_series(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch(pd.Series([2, 1], index=[0, 4], name='A'))

    expected = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([2, 1, 2, 3, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo1', 'foo2', 'foo3', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    for col, values in model.source.data.items():
        if col == 'D':
            expected_array = expected[col].astype(np.int64) / 10e5
        else:
            expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_scalars_not_as_index(document, comm):
    df = makeMixedDataFrame().sort_values('A', ascending=False)
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch({'A': [(0, 2), (4, 1)], 'C': [(0, 'foo0')]}, as_index=False)

    expected = {
        'index': np.array([4, 3, 2, 1, 0]),
        'A': np.array([2, 3, 2, 1, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo0', 'foo4', 'foo3', 'foo2', 'foo1']),
        'D': np.array(['2009-01-07T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-01T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    for col, values in model.source.data.items():
        if col == 'D':
            expected_array = expected[col].astype(np.int64) / 10e5
        else:
            expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_filters(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, filters=[{'field': 'A', 'type': '>', 'value': '2'}])

    model = table.get_root(document, comm)

    table.patch({'A': [(0, 2), (4, 1)], 'C': [(0, 'foo0')]})

    expected_df = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([2, 1, 2, 3, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo0', 'foo2', 'foo3', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    expected_src = {
        'index': np.array([3]),
        'A': np.array([3]),
        'B': np.array([1]),
        'C': np.array(['foo4']),
        'D': np.array(['2009-01-06T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected_src[col])
        if col != 'index':
            np.testing.assert_array_equal(
                table.value[col].values, expected_df[col]
            )

def test_tabulator_patch_with_sorters(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, sorters=[{'field': 'A', 'dir': 'desc'}])

    model = table.get_root(document, comm)

    table.patch({'A': [(0, 2), (4, 1)], 'C': [(0, 'foo0')]})

    expected_df = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([2, 1, 2, 3, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo0', 'foo2', 'foo3', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    expected_src = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([2., 1., 2., 3., 1.]),
        'B': np.array([0., 1., 0., 1., 0.]),
        'C': np.array(['foo0', 'foo2', 'foo3', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected_src[col])
        if col != 'index':
            np.testing.assert_array_equal(
                table.value[col].values, expected_df[col]
            )

def test_tabulator_patch_with_sorters_and_pagination(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(
        df, sorters=[{'field': 'A', 'dir': 'desc'}],
        pagination='remote', page_size=3, page=2
    )

    model = table.get_root(document, comm)

    table.patch({'A': [(0, 2), (4, 1)], 'C': [(0, 'foo0')]})

    expected_df = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([2, 1, 2, 3, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo0', 'foo2', 'foo3', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    expected_src = {
        'index': np.array([1, 4]),
        'A': np.array([1, 1]),
        'B': np.array([1, 0]),
        'C': np.array(['foo2', 'foo5']),
        'D': np.array(['2009-01-02T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected_src[col])
        if col != 'index':
            np.testing.assert_array_equal(
                table.value[col].values, expected_df[col]
            )

def test_tabulator_patch_ranges(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch({
        'A': [(slice(0, 5), [5, 4, 3, 2, 1])],
        'C': [(slice(0, 3), ['foo3', 'foo2', 'foo1'])]
    })

    expected = {
        'index': np.array([0, 1, 2, 3, 4]),
        'A': np.array([5, 4, 3, 2, 1]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo3', 'foo2', 'foo1', 'foo4', 'foo5']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    for col, values in model.source.data.items():
        if col == 'D':
            expected_array = expected[col].astype(np.int64) / 10e5
        else:
            expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])


def test_tabulator_stream_series_paginated_not_follow(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote', page_size=2)

    model = table.get_root(document, comm)

    stream_value = pd.Series({'A': 5, 'B': 1, 'C': 'foo6', 'D': dt.datetime(2009, 1, 8)})

    table.stream(stream_value, follow=False)

    assert table.page == 1
    assert len(table.value) == 6

    expected = {
        'index': np.array([0, 1]),
        'A': np.array([0, 1]),
        'B': np.array([0, 1]),
        'C': np.array(['foo1', 'foo2']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_stream_series_paginated_follow(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote', page_size=2)

    model = table.get_root(document, comm)

    stream_value = pd.Series({'A': 5, 'B': 1, 'C': 'foo6', 'D': dt.datetime(2009, 1, 8)})

    table.stream(stream_value, follow=True)

    assert table.page == 3
    assert len(table.value) == 6

    expected = {
        'index': np.array([4, 5]),
        'A': np.array([4, 5]),
        'B': np.array([0, 1]),
        'C': np.array(['foo5', 'foo6']),
        'D': np.array(['2009-01-07T00:00:00.000000000',
                       '2009-01-08T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_paginated_sorted_selection(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote', page_size=2)

    table.sorters = [{'field': 'A', 'dir': 'dec'}]

    model = table.get_root(document, comm)

    table.selection = [3]
    assert model.source.selected.indices == [1]

    table.selection = [0, 1]
    assert model.source.selected.indices == []

    table.selection = [3, 4]
    assert model.source.selected.indices == [1, 0]

    table.selection = []
    assert model.source.selected.indices == []

    table._process_events({'indices': [0, 1]})
    assert table.selection == [4, 3]

    table._process_events({'indices': [1]})
    assert table.selection == [3]

    table.sorters = [{'field': 'A', 'dir': 'asc'}]
    table._process_events({'indices': [1]})
    assert table.selection == [1]


def test_tabulator_stream_dataframe(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    stream_value = pd.DataFrame({
        'A': [5, 6],
        'B': [1, 0],
        'C': ['foo6', 'foo7'],
        'D': [dt.datetime(2009, 1, 8), dt.datetime(2009, 1, 9)]
    })

    table.stream(stream_value)

    assert len(table.value) == 7

    expected = {
        'index': np.array([0, 1, 2, 3, 4, 5, 6]),
        'A': np.array([0, 1, 2, 3, 4, 5, 6]),
        'B': np.array([0, 1, 0, 1, 0, 1, 0]),
        'C': np.array(['foo1', 'foo2', 'foo3', 'foo4', 'foo5', 'foo6', 'foo7']),
        'D': np.array(['2009-01-01T00:00:00.000000000',
                       '2009-01-02T00:00:00.000000000',
                       '2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000',
                       '2009-01-08T00:00:00.000000000',
                       '2009-01-09T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_constant_scalar_filter_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    table.filters = [{'field': 'C', 'type': '=', 'value': 'foo3'}]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'B': np.array([0.]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=np.array([2]))
    pd.testing.assert_frame_equal(table._processed, expected)

def test_tabulator_constant_scalar_filter_on_index_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    table.filters = [{'field': 'index', 'type': '=', 'value': 2}]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'B': np.array([0.]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=np.array([2]))
    pd.testing.assert_frame_equal(table._processed, expected)

def test_tabulator_constant_scalar_filter_on_multi_index_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']))

    table.filters = [
        {'field': 'A', 'type': '=', 'value': 2},
        {'field': 'C', 'type': '=', 'value': 'foo3'}
    ]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'C': np.array(['foo3']),
        'B': np.array([0.]),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    })
    pd.testing.assert_frame_equal(table._processed, expected)

def test_tabulator_constant_list_filter_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    table.filters = [{'field': 'C', 'type': 'in', 'value': ['foo3', 'foo5']}]

    expected = pd.DataFrame({
        'A': np.array([2, 4.]),
        'B': np.array([0, 0.]),
        'C': np.array(['foo3', 'foo5']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=np.array([2, 4]))
    pd.testing.assert_frame_equal(table._processed, expected)

def test_tabulator_keywords_filter_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    table.filters = [{'field': 'C', 'type': 'keywords', 'value': 'foo3 foo5'}]

    expected = pd.DataFrame({
        'A': np.array([2, 4.]),
        'B': np.array([0, 0.]),
        'C': np.array(['foo3', 'foo5']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=np.array([2, 4]))
    pd.testing.assert_frame_equal(table._processed, expected)

def test_tabulator_keywords_match_all_filter_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters={'C': {'type': 'input', 'func': 'keywords', 'matchAll': True}})

    table.filters = [{'field': 'C', 'type': 'keywords', 'value': 'f oo 3'}]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'B': np.array([0.]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=[2])
    pd.testing.assert_frame_equal(table._processed, expected)

def test_tabulator_constant_scalar_filter_with_pagination_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote')

    model = table.get_root(document, comm)

    table.filters = [{'field': 'C', 'type': '=', 'value': 'foo3'}]

    expected = {
        'index': np.array([2]),
        'A': np.array([2]),
        'B': np.array([0]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_constant_scalar_filter_on_index_with_pagination_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote')

    model = table.get_root(document, comm)

    table.filters = [{'field': 'index', 'type': '=', 'value': 2}]

    expected = {
        'index': np.array([2]),
        'A': np.array([2]),
        'B': np.array([0]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_constant_scalar_filter_on_multi_index_with_pagination_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']), pagination='remote')

    model = table.get_root(document, comm)

    table.filters = [
        {'field': 'A', 'type': '=', 'value': 2},
        {'field': 'C', 'type': '=', 'value': 'foo3'}
    ]

    expected = {
        'index': np.array([0]),
        'A': np.array([2]),
        'C': np.array(['foo3']),
        'B': np.array([0]),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_constant_list_filter_with_pagination_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote')

    model = table.get_root(document, comm)

    table.filters = [{'field': 'C', 'type': 'in', 'value': ['foo3', 'foo5']}]

    expected = {
        'index': np.array([2, 4]),
        'A': np.array([2, 4]),
        'B': np.array([0, 0]),
        'C': np.array(['foo3', 'foo5']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_keywords_filter_with_pagination_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote')

    model = table.get_root(document, comm)

    table.filters = [{'field': 'C', 'type': 'keywords', 'value': 'foo3 foo5'}]

    expected = {
        'index': np.array([2, 4]),
        'A': np.array([2, 4]),
        'B': np.array([0, 0]),
        'C': np.array(['foo3', 'foo5']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])


def test_tabulator_keywords_match_all_filter_with_pagination_client_side(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(
        df, header_filters={'C': {'type': 'input', 'func': 'keywords', 'matchAll': True}},
        pagination='remote'
    )

    model = table.get_root(document, comm)

    table.filters = [{'field': 'C', 'type': 'keywords', 'value': 'f oo 3'}]

    expected = {
        'index': np.array([2]),
        'A': np.array([2]),
        'B': np.array([0]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_constant_scalar_filter(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.add_filter('foo3', 'C')

    expected = {
        'index': np.array([2]),
        'A': np.array([2]),
        'B': np.array([0]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_widget_scalar_filter(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    widget = TextInput(value='foo3')
    table.add_filter(widget, 'C')

    expected = {
        'index': np.array([2]),
        'A': np.array([2]),
        'B': np.array([0]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

    widget.value = 'foo1'

    expected = {
        'index': np.array([0]),
        'A': np.array([0]),
        'B': np.array([0]),
        'C': np.array(['foo1']),
        'D': np.array(['2009-01-01T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_constant_list_filter(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.add_filter(['foo3', 'foo5'], 'C')

    expected = {
        'index': np.array([2, 4]),
        'A': np.array([2., 4.]),
        'B': np.array([0., 0.]),
        'C': np.array(['foo3', 'foo5']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_function_filter(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    widget = TextInput(value='foo3')

    def filter_c(df, value):
        return df[df.C.str.contains(value)]

    table.add_filter(bind(filter_c, value=widget), 'C')

    expected = {
        'index': np.array([2]),
        'A': np.array([2]),
        'B': np.array([0]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

    widget.value = 'foo1'

    expected = {
        'index': np.array([0]),
        'A': np.array([0]),
        'B': np.array([0]),
        'C': np.array(['foo1']),
        'D': np.array(['2009-01-01T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_constant_tuple_filter(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.add_filter((2, 3), 'A')

    expected = {
        'index': np.array([2, 3]),
        'A': np.array([2, 3]),
        'B': np.array([0, 1]),
        'C': np.array(['foo3', 'foo4']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-06T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_stream_dataframe_with_filter(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.add_filter(['foo2', 'foo7'], 'C')

    stream_value = pd.DataFrame({
        'A': [5, 6],
        'B': [1, 0],
        'C': ['foo6', 'foo7'],
        'D': [dt.datetime(2009, 1, 8), dt.datetime(2009, 1, 9)]
    })

    table.stream(stream_value)

    assert len(table.value) == 7

    expected = {
        'index': np.array([1, 6]),
        'A': np.array([1, 6]),
        'B': np.array([1, 0]),
        'C': np.array(['foo2', 'foo7']),
        'D': np.array(['2009-01-02T00:00:00.000000000',
                       '2009-01-09T00:00:00.000000000'],
                      dtype='datetime64[ns]').astype(np.int64) / 10e5
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_stream_dataframe_selectable_rows(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, selectable_rows=lambda df: list(range(0, len(df), 2)))

    model = table.get_root(document, comm)

    assert model.selectable_rows == [0, 2, 4]

    stream_value = pd.DataFrame({
        'A': [5, 6],
        'B': [1, 0],
        'C': ['foo6', 'foo7'],
        'D': [dt.datetime(2009, 1, 8), dt.datetime(2009, 1, 9)]
    })

    table.stream(stream_value)

    assert model.selectable_rows == [0, 2, 4, 6]

def test_tabulator_dataframe_replace_data(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.value = makeCustomDataframe(2, 2)

    assert len(model.columns) == 3
    c1, c2, c3 = model.columns
    assert c1.field == 'R0'
    assert c2.field == 'C_l0_g0'
    assert c3.field == 'C_l0_g1'
    assert model.configuration == {
        'columns': [{'field': 'R0'}, {'field': 'C_l0_g0'}, {'field': 'C_l0_g1'}],
        'selectable': True,
        'dataTree': False
    }
    expected = {
        'C_l0_g0': np.array(['R0C0', 'R1C0'], dtype=object),
        'C_l0_g1': np.array(['R0C1', 'R1C1'], dtype=object),
        'R0': np.array(['R_l0_g0', 'R_l0_g1'], dtype=object)
    }
    for col, values in model.source.data.items():
        np.testing.assert_array_equal(values, expected[col])

def test_tabulator_download_menu_default():
    df = makeMixedDataFrame()
    table = Tabulator(df)

    filename, button = table.download_menu()

    assert isinstance(filename, TextInput)
    assert isinstance(button, Button)

    assert filename.value == 'table.csv'
    assert filename.name == 'Filename'
    assert button.name == 'Download'

def test_tabulator_download_menu_custom_kwargs():
    df = makeMixedDataFrame()
    table = Tabulator(df)

    filename, button = table.download_menu(
        text_kwargs={'name': 'Enter filename', 'value': 'file.csv'},
        button_kwargs={'name': 'Download table'},
    )

    assert isinstance(filename, TextInput)
    assert isinstance(button, Button)

    assert filename.value == 'file.csv'
    assert filename.name == 'Enter filename'
    assert button.name == 'Download table'

def test_tabulator_patch_event():
    df = makeMixedDataFrame()
    table = Tabulator(df)

    values = []
    table.on_edit(lambda e: values.append((e.column, e.row, e.value)))

    for col in df.columns:
        for row in range(len(df)):
            event = TableEditEvent(model=None, column=col, row=row)
            table._process_event(event)
            assert values[-1] == (col, row, df[col].iloc[row])



def test_server_edit_event():
    df = makeMixedDataFrame()
    table = Tabulator(df)

    serve(table, port=7001, threaded=True, show=False)

    time.sleep(0.5)

    requests.get('http://localhost:7001')

    assert table._models
    ref, (model, _) = list(table._models.items())[0]
    doc = list(table._documents.keys())[0]

    events = []
    table.on_edit(lambda e: events.append(e))

    new_data = dict(model.source.data)
    new_data['B'][1] = 3.14

    table._server_change(doc, ref, None, 'data', model.source.data, new_data)
    table._server_event(doc, TableEditEvent(model, 'B', 1))

    time.sleep(0.1)
    assert len(events) == 1
    assert events[0].value == 3.14
    assert events[0].old == 1

def test_tabulator_cell_click_event():
    df = makeMixedDataFrame()
    table = Tabulator(df)

    values = []
    table.on_click(lambda e: values.append((e.column, e.row, e.value)))

    data = df.reset_index()
    for col in data.columns:
        for row in range(len(data)):
            event = CellClickEvent(model=None, column=col, row=row)
            table._process_event(event)
            assert values[-1] == (col, row, data[col].iloc[row])

def test_server_cell_click_async_event():
    df = makeMixedDataFrame()
    table = Tabulator(df)

    counts = []
    async def cb(event, count=[0]):
        import asyncio
        count[0] += 1
        counts.append(count[0])
        await asyncio.sleep(1)
        count[0] -= 1

    table.on_click(cb)

    port = 7002
    serve(table, port=port, threaded=True, show=False)

    # Wait for server to start
    time.sleep(1)

    requests.get(f"http://localhost:{port}/")

    data = df.reset_index()
    doc = list(table._models.values())[0][0].document
    with set_curdoc(doc):
        for col in data.columns:
            for row in range(len(data)):
                event = CellClickEvent(model=None, column=col, row=row)
                table._process_event(event)

    # Wait for callbacks to be scheduled
    time.sleep(2)

    # Ensure multiple callbacks started concurrently
    assert max(counts) > 1

def test_tabulator_pagination_remote_cell_click_event():
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote', page_size=2)

    values = []
    table.on_click(lambda e: values.append((e.column, e.row, e.value)))

    data = df.reset_index()
    for col in data.columns:
        for p in range(len(df)//2):
            table.page = p+1
            for row in range(2):
                event = CellClickEvent(model=None, column=col, row=row)
                table._process_event(event)
                assert values[-1] == (col, (p*2)+row, data[col].iloc[(p*2)+row])
