import asyncio
import datetime as dt
import random
import string

from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import param
import pytest

from bokeh.models.widgets.tables import (
    AvgAggregator, CellEditor, CheckboxEditor, DataCube, DateEditor,
    DateFormatter, HTMLTemplateFormatter, IntEditor, MinAggregator,
    NumberEditor, NumberFormatter, SelectEditor, StringEditor, StringFormatter,
    SumAggregator,
)
from packaging.version import Version

from panel.depends import bind
from panel.io.state import set_curdoc
from panel.models.tabulator import CellClickEvent, TableEditEvent
from panel.tests.util import mpl_available, serve_and_request, wait_until
from panel.widgets import Button, TextInput
from panel.widgets.tables import DataFrame, Tabulator

pd_old = pytest.mark.skipif(Version(pd.__version__) < Version('1.3'),
                            reason="Requires latest pandas")


def makeMixedDataFrame():
    data = {
        "A": [0.0, 1.0, 2.0, 3.0, 4.0],
        "B": [0.0, 1.0, 0.0, 1.0, 0.0],
        "C": ["foo1", "foo2", "foo3", "foo4", "foo5"],
        "D": pd.bdate_range("1/1/2009", periods=5),
    }
    return pd.DataFrame(data)


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
    df = pd.DataFrame({'int': [1, 2, 3]}, index=pd.date_range('2000-01-01', periods=3))
    table = DataFrame(df)

    model = table.get_root(document, comm)

    dt_col, _ = model.columns

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


@pytest.mark.parametrize('widget', [DataFrame, Tabulator])
def test_dataframe_process_data_no_unsync(dataframe, widget):
    df = dataframe.copy()

    table1 = widget(dataframe.copy())
    table2 = widget(table1.param.value.rx().copy())
    table1._process_events({'data': {'int': [5, 7, 9]}})
    df['int'] = [5, 7, 9]
    pd.testing.assert_frame_equal(table1.value, df)
    pd.testing.assert_frame_equal(table2.value, df)

    # Simulate edit to unsync
    table2._process_events({'data': {'int': [3, 2, 4]}})

    table1.value = dataframe.copy()
    pd.testing.assert_frame_equal(table2.value, dataframe)


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


@pytest.fixture
def df_agg():
    df = pd.DataFrame([
        ('Germany', 2020, 9, 2.4, 'A'),
        ('Germany', 2021, 3, 7.3, 'C'),
        ('Germany', 2022, 6, 3.1, 'B'),
        ('UK', 2020, 5, 8.0, 'A'),
        ('UK', 2021, 1, 3.9, 'B'),
        ('UK', 2022, 9, 2.2, 'A')
    ], columns=['Country', 'Year', 'Int', 'Float', 'Str']).set_index(['Country', 'Year'])
    return df


def test_hierarchical_index(document, comm, df_agg):
    table = DataFrame(value=df_agg, hierarchical=True,
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


def test_tabulator_none_value(document, comm):
    table = Tabulator(value=None)
    assert table.indexes == []

    model = table.get_root(document, comm)

    assert model.source.data == {}
    assert model.columns == []


def test_tabulator_update_none_value(document, comm, df_mixed):
    table = Tabulator(value=df_mixed)

    model = table.get_root(document, comm)

    table.value = None

    assert model.source.data == {}
    assert model.columns == []


def test_tabulator_selection_resets():
    df = makeMixedDataFrame()
    table = Tabulator(df, selection=list(range(len(df))))

    for i in reversed(range(len(df))):
        table.value = df.iloc[:i]
        assert table.selection == list(range(i))


def test_tabulator_selected_dataframe():
    df = makeMixedDataFrame()
    table = Tabulator(df, selection=[0, 2])

    pd.testing.assert_frame_equal(table.selected_dataframe, df.iloc[[0, 2]])


def test_tabulator_multi_index(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']))

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'A', 'sorter': 'number'},
        {'field': 'C'},
        {'field': 'B', 'sorter': 'number'},
        {'field': 'D', 'sorter': 'timestamp'}
    ]

    assert np.array_equal(model.source.data['A'], np.array([0., 1., 2., 3., 4.]))
    assert np.array_equal(model.source.data['C'], np.array(['foo1', 'foo2', 'foo3', 'foo4', 'foo5']))


def test_tabulator_multi_index_hide_index(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']), show_index=False)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'B', 'sorter': 'number'},
        {'field': 'D', 'sorter': 'timestamp'}
    ]


def test_tabulator_multi_index_remote_pagination(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']), pagination='remote', page_size=3)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'A', 'sorter': 'number'},
        {'field': 'C'},
        {'field': 'B', 'sorter': 'number'},
        {'field': 'D', 'sorter': 'timestamp'}
    ]

    assert np.array_equal(model.source.data['A'], np.array([0., 1., 2.]))
    assert np.array_equal(model.source.data['C'], np.array(['foo1', 'foo2', 'foo3']))


def test_tabulator_multi_index_columns(document, comm):
    level_1 = ['A', 'A', 'A', 'B', 'B', 'B']
    level_2 = ['one', 'one', 'two', 'two', 'three', 'three']
    level_3 = ['X', 'Y', 'X', 'Y', 'X', 'Y']

    # Combine these into a MultiIndex
    multi_index = pd.MultiIndex.from_arrays([level_1, level_2, level_3], names=['Level 1', 'Level 2', 'Level 3'])

    # Create a DataFrame with this MultiIndex as columns
    df = pd.DataFrame(np.random.randn(4, 6), columns=multi_index)

    formatters = {('A', 'one', 'Y'): NumberFormatter(format='0.0000')}
    text_align = {('A', 'two', 'X'): 'left'}
    titles = {}
    widths = {}
    frozen_columns = []
    header_tooltips = {('A', 'one', 'Y'): 'Tooltips 1'}
    header_align = {('A', 'one', 'X'): 'left'}
    sortable = {('B', 'three', 'X'): False}
    title_formatters = {('B', 'three', 'Y'): {'type': 'star', 'stars': 5}}

    table = Tabulator(
        df,
        show_index=True,
        formatters=formatters,
        text_align=text_align,
        titles=titles,
        widths=widths,
        frozen_columns=frozen_columns,
        header_tooltips=header_tooltips,
        header_align=header_align,
        sortable=sortable,
        title_formatters=title_formatters,
    )

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number', 'headerSort': True},
        {
            'title': 'A',
            'columns': [
                {
                    'title': 'one',
                    'columns': [
                        {'field': 'A_one_X', 'sorter': 'number', 'headerHozAlign': 'left', 'headerSort': True},
                        {'field': 'A_one_Y', 'sorter': 'number', 'headerTooltip': 'Tooltips 1', 'headerSort': True},
                    ],
                },
                {'title': 'two', 'columns': [{'field': 'A_two_X', 'sorter': 'number', 'hozAlign': 'left', 'headerSort': True}]},
            ],
        },
        {
            'title': 'B',
            'columns': [
                {'title': 'two', 'columns': [{'field': 'B_two_Y', 'sorter': 'number', 'headerSort': True}]},
                {
                    'title': 'three',
                    'columns': [
                        {'field': 'B_three_X', 'sorter': 'number', 'headerSort': False},
                        {'field': 'B_three_Y', 'sorter': 'number', 'titleFormatter': 'star', 'titleFormatterParams': {'stars': 5}, 'headerSort': True},
                    ],
                },
            ],
        },
    ]

    assert model.columns[2].field == 'A_one_Y'
    mformatter = model.columns[2].formatter
    assert isinstance(mformatter, NumberFormatter)
    assert mformatter.format == '0.0000'

    for field in ("index", "A_one_X", "A_one_Y", "A_two_X", "B_two_Y", "B_three_X", "B_three_Y"):
        assert field in model.source.data


def test_tabulator_multi_index_columns_hide_index(document, comm):
    level_1 = ['A', 'A', 'A', 'B', 'B', 'B']
    level_2 = ['one', 'one', 'two', 'two', 'three', 'three']
    level_3 = ['X', 'Y', 'X', 'Y', 'X', 'Y']

    # Combine these into a MultiIndex
    multi_index = pd.MultiIndex.from_arrays([level_1, level_2, level_3], names=['Level 1', 'Level 2', 'Level 3'])

    # Create a DataFrame with this MultiIndex as columns
    df = pd.DataFrame(np.random.randn(4, 6), columns=multi_index)

    table = Tabulator(df, show_index=False)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'title': 'A', 'columns': [
            {'title': 'one', 'columns': [
                {'field': 'A_one_X', 'sorter': 'number'},
                {'field': 'A_one_Y', 'sorter': 'number'},
            ]},
            {'title': 'two', 'columns': [
                {'field': 'A_two_X', 'sorter': 'number'}
            ]},
        ]},
        {'title': 'B', 'columns': [
            {'title': 'two', 'columns': [
                {'field': 'B_two_Y', 'sorter': 'number'},
            ]},
            {'title': 'three', 'columns': [
                {'field': 'B_three_X', 'sorter': 'number'},
                {'field': 'B_three_Y', 'sorter': 'number'}
            ]},
        ]}
    ]
    for field in ("A_one_X", "A_one_Y", "A_two_X", "B_two_Y", "B_three_X", "B_three_Y"):
        assert field in model.source.data


def test_tabulator_multi_index_multi_index_columns(document, comm):
    level_1 = ['A', 'A', 'A', 'B', 'B', 'B']
    level_2 = ['one', 'one', 'two', 'two', 'three', 'three']
    level_3 = ['X', 'Y', 'X', 'Y', 'X', 'Y']

    # Combine these into a MultiIndex
    multi_columns = pd.MultiIndex.from_arrays([level_1, level_2, level_3], names=['Level 1', 'Level 2', 'Level 3'])

    # Create multiIndex
    numbers = [0, 1, 2]
    colors = ['green', 'purple']
    multi_index = pd.MultiIndex.from_product([numbers, colors], names=['number', 'color'])

    # Create a DataFrame with MultiIndex as columns and MultiIndex as index
    df = pd.DataFrame(np.random.randn(6, 6), index=multi_index, columns=multi_columns)

    table = Tabulator(
        df,
        show_index=True,
        titles={
            ("A",): "Title a",
            ("A", "two"): "Title two",
            ("A", "two", "X"): "New title",
        },
    )

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'number__', 'sorter': 'number'},
        {'field': 'color__'},
        {'title': 'Title a', 'columns': [
            {'title': 'one', 'columns': [
                {'field': 'A_one_X', 'sorter': 'number'},
                {'field': 'A_one_Y', 'sorter': 'number'},
            ]},
            {'title': 'Title two', 'columns': [
                {'field': 'A_two_X', 'sorter': 'number'}
            ]},
        ]},
        {'title': 'B', 'columns': [
            {'title': 'two', 'columns': [
                {'field': 'B_two_Y', 'sorter': 'number'},
            ]},
            {'title': 'three', 'columns': [
                {'field': 'B_three_X', 'sorter': 'number'},
                {'field': 'B_three_Y', 'sorter': 'number'}
            ]},
        ]}
    ]
    for field in ("number__", "color__", "A_one_X", "A_one_Y", "A_two_X", "B_two_Y", "B_three_X", "B_three_Y"):
        assert field in model.source.data

    assert(model.columns[4].field == "A_two_X")
    assert(model.columns[4].title == "New title")

def test_tabulator_multi_index_multi_index_columns_hide_index(document, comm):
    level_1 = ['A', 'A', 'A', 'B', 'B', 'B']
    level_2 = ['one', 'one', 'two', 'two', 'three', 'three']
    level_3 = ['X', 'Y', 'X', 'Y', 'X', 'Y']

    # Combine these into a MultiIndex
    multi_columns = pd.MultiIndex.from_arrays([level_1, level_2, level_3], names=['Level 1', 'Level 2', 'Level 3'])

    # Create multiIndex
    numbers = [0, 1, 2]
    colors = ['green', 'purple']
    multi_index = pd.MultiIndex.from_product([numbers, colors], names=['number', 'color'])

    # Create a DataFrame with MultiIndex as columns and MultiIndex as index
    df = pd.DataFrame(np.random.randn(6, 6), index=multi_index, columns=multi_columns)

    table = Tabulator(df, show_index=False)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'title': 'A', 'columns': [
            {'title': 'one', 'columns': [
                {'field': 'A_one_X', 'sorter': 'number'},
                {'field': 'A_one_Y', 'sorter': 'number'},
            ]},
            {'title': 'two', 'columns': [
                {'field': 'A_two_X', 'sorter': 'number'}
            ]},
        ]},
        {'title': 'B', 'columns': [
            {'title': 'two', 'columns': [
                {'field': 'B_two_Y', 'sorter': 'number'},
            ]},
            {'title': 'three', 'columns': [
                {'field': 'B_three_X', 'sorter': 'number'},
                {'field': 'B_three_Y', 'sorter': 'number'}
            ]},
        ]}
    ]
    for field in ("A_one_X", "A_one_Y", "A_two_X", "B_two_Y", "B_three_X", "B_three_Y"):
        assert field in model.source.data


def test_tabulator_expanded_content(document, comm):
    df = makeMixedDataFrame()

    table = Tabulator(df, expanded=[0, 1], row_content=lambda r: r.A)

    model = table.get_root(document, comm)

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


def test_tabulator_remote_paginated_expanded_content(document, comm):
    df = makeMixedDataFrame()

    table = Tabulator(
        df, expanded=[0, 4], row_content=lambda r: r.A, pagination='remote', page_size=3
    )

    model = table.get_root(document, comm)

    assert len(model.children) == 1
    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;0.0&lt;/pre&gt;"

    table.page = 2

    assert len(model.children) == 1
    assert 1 in model.children
    row1 = model.children[1]
    assert row1.text == "&lt;pre&gt;4.0&lt;/pre&gt;"


def test_tabulator_remote_sorted_paginated_expanded_content(document, comm):
    df = makeMixedDataFrame()

    table = Tabulator(
        df, expanded=[0, 1], row_content=lambda r: r.A, pagination='remote', page_size=2,
        sorters = [{'field': 'A', 'sorter': 'number', 'dir': 'desc'}], page=3
    )

    model = table.get_root(document, comm)

    assert len(model.children) == 1
    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;0.0&lt;/pre&gt;"

    table.page = 2

    assert len(model.children) == 1
    assert 1 in model.children
    row1 = model.children[1]
    assert row1.text == "&lt;pre&gt;1.0&lt;/pre&gt;"

    table.expanded = [0, 1, 2]

    assert len(model.children) == 2
    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;2.0&lt;/pre&gt;"


def test_tabulator_filtered_expanded_content_remote_pagination(document, comm):
    df = makeMixedDataFrame()

    table = Tabulator(
        df,
        expanded=[0, 1, 2, 3],
        filters=[{'field': 'B', 'sorter': 'number', 'type': '=', 'value': '1.0'}],
        pagination='remote',
        row_content=lambda r: r.A,
    )

    model = table.get_root(document, comm)

    assert len(model.children) == 2

    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;1.0&lt;/pre&gt;"

    assert 1 in model.children
    row1 = model.children[1]
    assert row1.text == "&lt;pre&gt;3.0&lt;/pre&gt;"

    model.expanded = [0]
    assert table.expanded == [1]

    table.filters = [{'field': 'B', 'sorter': 'number', 'type': '=', 'value': '0'}]

    assert not model.expanded
    assert table.expanded == [1]

    table.expanded = [0, 1]

    assert len(model.children) == 1

    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;0.0&lt;/pre&gt;"


@pytest.mark.parametrize('pagination', ['local', None])
def test_tabulator_filtered_expanded_content(document, comm, pagination):
    df = makeMixedDataFrame()

    table = Tabulator(
        df,
        expanded=[0, 1, 2, 3],
        filters=[{'field': 'B', 'sorter': 'number', 'type': '=', 'value': '1.0'}],
        pagination=pagination,
        row_content=lambda r: r.A,
    )

    model = table.get_root(document, comm)

    assert len(model.children) == 4

    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;0.0&lt;/pre&gt;"

    assert 1 in model.children
    row1 = model.children[1]
    assert row1.text == "&lt;pre&gt;1.0&lt;/pre&gt;"

    assert 2 in model.children
    row2 = model.children[2]
    assert row2.text == "&lt;pre&gt;2.0&lt;/pre&gt;"

    assert 3 in model.children
    row3 = model.children[3]
    assert row3.text == "&lt;pre&gt;3.0&lt;/pre&gt;"

    model.expanded = [1]
    assert table.expanded == [1]

    table.filters = [{'field': 'B', 'sorter': 'number', 'type': '=', 'value': '0'}]

    assert model.expanded == [1]
    assert table.expanded == [1]

    table.expanded = [0, 1]

    assert len(model.children) == 2

    assert 0 in model.children
    row0 = model.children[0]
    assert row0.text == "&lt;pre&gt;0.0&lt;/pre&gt;"

    assert 1 in model.children
    row1 = model.children[1]
    assert row1.text == "&lt;pre&gt;1.0&lt;/pre&gt;"


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


def test_tabulator_expanded_content_pagination(document, comm):
    df = makeMixedDataFrame()

    table = Tabulator(df, expanded=[0, 1], row_content=lambda r: r.A, pagination='remote', page_size=2)

    model = table.get_root(document, comm)

    assert len(model.children) == 2

    table.page = 2

    assert len(model.children) == 0


def test_tabulator_content_embed(document, comm):
    df = makeMixedDataFrame()

    table = Tabulator(df, embed_content=True, row_content=lambda r: r.A)

    model = table.get_root(document, comm)

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


def test_tabulator_content_embed_and_expand(document, comm):
    # https://github.com/holoviz/panel/issues/6200
    df = makeMixedDataFrame()

    calls = []
    def row_content(row):
        calls.append(row)
        return row.A

    table = Tabulator(df, embed_content=True, row_content=row_content)

    model = table.get_root(document, comm)

    assert len(calls) == len(df)

    assert len(model.children) == len(df)

    for i, r in df.iterrows():
        assert i in model.children
        row = model.children[i]
        assert row.text  == f"&lt;pre&gt;{r.A}&lt;/pre&gt;"

    # Expanding a row should not call row_content again in this context.
    table.expanded = [1]

    assert len(calls) == len(df)


def test_tabulator_selected_and_filtered_dataframe(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, selection=list(range(len(df))))

    pd.testing.assert_frame_equal(table.selected_dataframe, df)

    table.add_filter('foo3', 'C')

    assert table.selection == list(range(5))

    pd.testing.assert_frame_equal(table.selected_dataframe, df[df["C"] == "foo3"])

    table.remove_filter('foo3')

    table.selection = [0, 1, 2]

    table.add_filter('foo3', 'C')

    assert table.selection == [0, 1, 2]


@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_selection_indices_on_remote_paginated_and_filtered_data(document, comm, df_strings, pagination):
    tbl = Tabulator(
        df_strings,
        pagination=pagination,
        page_size=6,
        show_index=False,
        height=300,
        width=400
    )

    descr_filter = TextInput(name='descr')

    def contains_filter(df, pattern=None):
        if not pattern:
            return df
        return df[df.descr.str.contains(pattern, case=False)]

    filter_fn = param.bind(contains_filter, pattern=descr_filter)
    tbl.add_filter(filter_fn)

    model = tbl.get_root(document, comm)

    descr_filter.value = 'cut'

    pd.testing.assert_frame_equal(
        tbl.current_view, df_strings[df_strings.descr.str.contains('cut', case=False)]
    )

    model.source.selected.indices = [0, 2]

    assert tbl.selection == [3, 8]

    model.page_size = 2
    model.source.selected.indices = [1]

    assert tbl.selection == [7]


def test_tabulator_config_defaults(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number'},
        {'field': 'A', 'sorter': 'number'},
        {'field': 'B', 'sorter': 'number'},
        {'field': 'C'},
        {'field': 'D', 'sorter': 'timestamp'}
    ]
    assert model.configuration['selectable'] == True

def test_tabulator_config_widths_percent(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, widths={'A': '22%', 'B': 100})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number'},
        {'field': 'A', 'sorter': 'number', 'width': '22%'},
        {'field': 'B', 'sorter': 'number'},
        {'field': 'C'},
        {'field': 'D', 'sorter': 'timestamp'}
    ]
    assert model.columns[2].width == 100

def test_tabulator_header_filters_config_boolean(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters=True)

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number', 'headerFilter': 'number'},
        {'field': 'A', 'sorter': 'number', 'headerFilter': True},
        {'field': 'B', 'sorter': 'number', 'headerFilter': True},
        {'field': 'C', 'headerFilter': True},
        {'field': 'D', 'headerFilter': False, 'sorter': 'timestamp'} # Datetime header filtering not supported
    ]

def test_tabulator_header_filters_column_config_list(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters={'C': 'list'})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number'},
        {'field': 'A', 'sorter': 'number'},
        {'field': 'B', 'sorter': 'number'},
        {'field': 'C', 'headerFilter': 'list', 'headerFilterParams': {'valuesLookup': True}, 'headerFilterFunc': 'like'},
        {'field': 'D', 'sorter': 'timestamp'}
    ]
    assert model.configuration['selectable'] == True

@pytest.mark.parametrize('editor', ['select', 'autocomplete'])
def test_tabulator_header_filters_column_config_select_autocomplete_backwards_compat(document, comm, editor):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters={
        'C': editor,
        'D': {'type': editor, 'values': True, 'multiselect': True}
    })

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number'},
        {'field': 'A', 'sorter': 'number'},
        {'field': 'B', 'sorter': 'number'},
        {'field': 'C', 'headerFilter': 'list', 'headerFilterParams': {'valuesLookup': True}, 'headerFilterFunc': 'like'},
        {'field': 'D', 'headerFilter': 'list', 'headerFilterParams': {'valuesLookup': True, 'multiselect': True}, 'sorter': 'timestamp', 'headerFilterFunc': 'in'},
    ]
    assert model.configuration['selectable'] == True

def test_tabulator_header_filters_column_config_dict(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, header_filters={
        'C': {'type': 'list', 'valuesLookup': True, 'func': '!=', 'placeholder': 'Not equal'}
    })

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number'},
        {'field': 'A', 'sorter': 'number'},
        {'field': 'B', 'sorter': 'number'},
        {
            'field': 'C',
            'headerFilter': 'list',
            'headerFilterParams': {'valuesLookup': True},
            'headerFilterFunc': '!=',
            'headerFilterPlaceholder': 'Not equal'
        },
        {'field': 'D', 'sorter': 'timestamp'}
    ]
    assert model.configuration['selectable'] == True


def test_tabulator_editors_default(document, comm):
    df = pd.DataFrame({
        'int': [1, 2],
        'float': [3.14, 6.28],
        'str': ['A', 'B'],
        'date': [dt.date(2009, 1, 8), dt.date(2010, 1, 8)],
        'datetime': [dt.datetime(2009, 1, 8), dt.datetime(2010, 1, 8)],
        'bool': [True, False],
    })
    table = Tabulator(df)
    model = table.get_root(document, comm)
    assert isinstance(model.columns[1].editor, IntEditor)
    assert isinstance(model.columns[2].editor, NumberEditor)
    assert isinstance(model.columns[3].editor, StringEditor)
    assert isinstance(model.columns[4].editor, DateEditor)
    assert isinstance(model.columns[5].editor, DateEditor)
    assert isinstance(model.columns[6].editor, CheckboxEditor)


def test_tabulator_formatters_default(document, comm):
    df = pd.DataFrame({
        'int': [1, 2],
        'float': [3.14, 6.28],
        'str': ['A', 'B'],
        'date': [dt.date(2009, 1, 8), dt.date(2010, 1, 8)],
        'datetime': [dt.datetime(2009, 1, 8), dt.datetime(2010, 1, 8)],
    })
    table = Tabulator(df)
    model = table.get_root(document, comm)
    mformatter = model.columns[1].formatter
    assert isinstance(mformatter, NumberFormatter)
    mformatter = model.columns[2].formatter
    assert isinstance(mformatter, NumberFormatter)
    assert mformatter.format == '0,0.0[00000]'
    mformatter = model.columns[3].formatter
    assert isinstance(mformatter, StringFormatter)
    mformatter = model.columns[4].formatter
    assert isinstance(mformatter, DateFormatter)
    assert mformatter.format == '%Y-%m-%d'
    mformatter = model.columns[5].formatter
    assert isinstance(mformatter, DateFormatter)
    assert mformatter.format == '%Y-%m-%d %H:%M:%S'


def test_tabulator_config_formatter_string(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, formatters={'B': 'tickCross'})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'sorter': 'number', 'formatter': 'tickCross'}


def test_tabulator_config_formatter_dict(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, formatters={'B': {'type': 'tickCross', 'tristate': True}})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'sorter': 'number', 'formatter': 'tickCross', 'formatterParams': {'tristate': True}}


def test_tabulator_config_editor_string_backwards_compat(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, editors={'B': 'select'})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'sorter': 'number', 'editor': 'list'}


def test_tabulator_config_editor_string(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, editors={'B': 'list'})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'sorter': 'number', 'editor': 'list'}


def test_tabulator_config_editor_dict(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, editors={'B': {'type': 'list', 'valuesLookup': True}})

    model = table.get_root(document, comm)

    assert model.configuration['columns'][2] == {'field': 'B', 'sorter': 'number', 'editor': 'list', 'editorParams': {'valuesLookup': True}}


def test_tabulator_sortable_bool(dataframe, document, comm):
    table = Tabulator(dataframe, sortable=False)
    model = table.get_root(document, comm)
    assert not any(col['headerSort'] for col in model.configuration['columns'])


def test_tabulator_sortable_dict(dataframe, document, comm):
    table = Tabulator(dataframe, sortable={'int': False})
    model = table.get_root(document, comm)
    assert all(not col['headerSort'] if col['field'] == 'int' else col['headerSort']
               for col in model.configuration['columns'])


def test_tabulator_groups(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, groups={'Number': ['A', 'B'], 'Other': ['C', 'D']})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number'},
        {'title': 'Number',
         'columns': [
            {'field': 'A', 'sorter': 'number'},
            {'field': 'B', 'sorter': 'number'}
        ]},
        {'title': 'Other',
         'columns': [
            {'field': 'C'},
            {'field': 'D', 'sorter': 'timestamp'}
        ]}
    ]


def test_tabulator_numeric_groups(document, comm):
    df = pd.DataFrame(np.random.rand(10, 3))
    table = Tabulator(df, groups={'Number': [0, 1]})

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number'},
        {'title': 'Number',
         'columns': [
            {'field': '0', 'sorter': 'number'},
            {'field': '1', 'sorter': 'number'}
        ]},
        {'field': '2', 'sorter': 'number'}
    ]


def test_tabulator_frozen_cols(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, frozen_columns=['index'])

    model = table.get_root(document, comm)

    assert model.configuration['columns'] == [
        {'field': 'index', 'sorter': 'number', 'frozen': True},
        {'field': 'A', 'sorter': 'number'},
        {'field': 'B', 'sorter': 'number'},
        {'field': 'C'},
        {'field': 'D', 'sorter': 'timestamp'}
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


def test_tabulator_selectable_rows_nonallowed_selection_error(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, selectable_rows=lambda df: [0])

    model = table.get_root(document, comm)
    assert model.selectable_rows == [0]

    err_msg = (
        "Values in 'selection' must not have values "
        "which are not available with 'selectable_rows'."
    )

    # This is available with selectable rows
    table.selection = []
    assert table.selection == []
    table.selection = [0]
    assert table.selection == [0]

    # This is not and should raise the error
    with pytest.raises(ValueError, match=err_msg):
        table.selection = [1]
    assert table.selection == [0]
    with pytest.raises(ValueError, match=err_msg):
        table.selection = [0, 1]
    assert table.selection == [0]

    # No selectable_rows everything should work
    table = Tabulator(df)
    table.selection = []
    assert table.selection == []
    table.selection = [0]
    assert table.selection == [0]
    table.selection = [1]
    assert table.selection == [1]
    table.selection = [0, 1]
    assert table.selection == [0, 1]


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

    table.style.map(high_red, subset=['A'])

    model = table.get_root(document, comm)

    assert model.cell_styles['data'] == {
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
    assert df.columns.dtype == np.int64
    table = Tabulator(df)

    table.sorters = [{'field': 'index', 'sorter': 'number', 'dir': 'desc'}]
    res = table.current_view
    exp = df.sort_index(ascending=False)
    exp.columns = exp.columns.astype(object)

    pd.testing.assert_frame_equal(res, exp)
    assert df.columns.dtype == np.int64

def test_tabulator_sorters_int_name_column(document, comm):
    df = pd.DataFrame(np.random.rand(10, 4))
    assert df.columns.dtype == np.int64
    table = Tabulator(df)

    table.sorters = [{'field': '0', 'dir': 'desc'}]
    res = table.current_view
    exp = df.sort_values([0], ascending=False)
    exp.columns = exp.columns.astype(object)

    pd.testing.assert_frame_equal(res, exp)
    assert df.columns.dtype == np.int64


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

    stream_value = pd.DataFrame({'A': [5], 'B': [1], 'C': ['foo6'], 'D': [np.datetime64(dt.datetime(2009, 1, 8))]})

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

def test_tabulator_patch_with_dataframe_custom_index(document, comm):
    df = pd.DataFrame(dict(A=[1, 4, 2]), index=['foo1', 'foo2', 'foo3'])
    df_patch = pd.DataFrame(dict(A=[10]), index=['foo2'])

    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch(df_patch)

    expected = {
        'index': np.array(['foo1', 'foo2', 'foo3']),
        'A': np.array([1, 10, 2]),
    }
    for col, values in model.source.data.items():
        expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_dataframe_custom_index_name(document, comm):
    df = pd.DataFrame(dict(A=[1, 4, 2]), index=['foo1', 'foo2', 'foo3'])
    df.index.name = 'foo'
    df_patch = pd.DataFrame(dict(A=[10]), index=['foo2'])
    df.index.name = 'foo'

    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch(df_patch)

    expected = {
        'foo': np.array(['foo1', 'foo2', 'foo3']),
        'A': np.array([1, 10, 2]),
    }
    for col, values in model.source.data.items():
        expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'foo':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_complete_dataframe_custom_index(document, comm):
    df = makeMixedDataFrame()[['A', 'B', 'C']]
    df.index = [0, 1, 2, 3, 10]

    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch(df)

    expected = {
        'index': np.array([0, 1, 2, 3, 10]),
        'A': np.array([0, 1, 2, 3, 4]),
        'B': np.array([0, 1, 0, 1, 0]),
        'C': np.array(['foo1', 'foo2', 'foo3', 'foo4', 'foo5']),
    }
    for col, values in model.source.data.items():
        expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_dataframe_custom_index_multiple_error(document, comm):
    df = pd.DataFrame(dict(A=[1, 4, 2]), index=['foo1', 'foo1', 'foo3'])
    # Copy to assert at the end that the original dataframe hasn't been touched
    original = df.copy()
    df_patch = pd.DataFrame(dict(A=[20, 10]), index=['foo1', 'foo1'])

    table = Tabulator(df)

    with pytest.raises(
        ValueError,
        match=r"Patching a table with duplicate index values is not supported\. Found this duplicate index: 'foo1'"
    ):
        table.patch(df_patch)

    pd.testing.assert_frame_equal(table.value, original)

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
    table = Tabulator(df, filters=[{'field': 'A', 'sorter': 'number', 'type': '>', 'value': '2'}])

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

    table.filters = []

    for col, values in model.source.data.items():
        expected = expected_df[col]
        if col == 'D':
            expected = expected.astype(np.int64) / 10e5
        np.testing.assert_array_equal(values, expected)

def test_tabulator_patch_with_sorters(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, sorters=[{'field': 'A', 'sorter': 'number', 'dir': 'desc'}])

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
        df, sorters=[{'field': 'A', 'sorter': 'number', 'dir': 'desc'}],
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

def test_tabulator_patch_with_timestamp(document, comm):
    # https://github.com/holoviz/panel/issues/5555
    df = pd.DataFrame(dict(A=pd.to_datetime(['1980-01-01', '1980-01-02'])))
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch({'A': [(0, pd.Timestamp('2021-01-01'))]})

    expected = {
        'index': np.array([0, 1]),
        'A': np.array(['2021-01-01T00:00:00.000000000',
                       '1980-01-02T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }
    for col, values in model.source.data.items():
        if col == 'A':
            expected_array = expected[col].astype(np.int64) / 10e5
        else:
            expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        if col != 'index':
            np.testing.assert_array_equal(table.value[col].values, expected[col])

def test_tabulator_patch_with_NaT(document, comm):
    df = pd.DataFrame(dict(A=pd.to_datetime(['1980-01-01', np.nan])))
    assert df.loc[1, 'A'] is pd.NaT
    table = Tabulator(df)

    model = table.get_root(document, comm)

    table.patch({'A': [(0, pd.NaT)]})

    # We're also checking that the NaT value that was in the original table
    # at .loc[1, 'A'] is converted in the model as np.nan.
    expected = {
        'index': np.array([0, 1]),
        'A': np.array([np.nan, np.nan])
    }
    for col, values in model.source.data.items():
        expected_array = expected[col]
        np.testing.assert_array_equal(values, expected_array)
        # Not checking that the data in table.value is the same as expected
        # In table.value we have NaT values, in expected np.nan.


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

    table.sorters = [{'field': 'A', 'sorter': 'number', 'dir': 'dec'}]

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

    table.sorters = [{'field': 'A', 'sorter': 'number', 'dir': 'asc'}]
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

@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_tabulator_constant_scalar_filter_client_side(document, comm, pagination):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination=pagination)

    table.filters = [{'field': 'C', 'type': '=', 'value': 'foo3'}]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'B': np.array([0.]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=[2])
    pd.testing.assert_frame_equal(
        table._processed, expected if pagination == 'remote' else df
    )

@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_tabulator_constant_scalar_filter_on_index_client_side(document, comm, pagination):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination=pagination)

    table.filters = [{'field': 'index', 'sorter': 'number', 'type': '=', 'value': 2}]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'B': np.array([0.]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=[2])
    pd.testing.assert_frame_equal(
        table._processed, expected if pagination == 'remote' else df
    )

@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_tabulator_constant_scalar_filter_on_multi_index_client_side(document, comm, pagination):
    df = makeMixedDataFrame().set_index(['A', 'C'])
    table = Tabulator(df, pagination=pagination)

    table.filters = [
        {'field': 'A', 'sorter': 'number', 'type': '=', 'value': 2},
        {'field': 'C', 'type': '=', 'value': 'foo3'}
    ]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'C': np.array(['foo3']),
        'B': np.array([0.]),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }).set_index(['A', 'C'])
    pd.testing.assert_frame_equal(
        table._processed, expected if pagination == 'remote' else df
    )

@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_tabulator_constant_list_filter_client_side(document, comm, pagination):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination=pagination)

    table.filters = [{'field': 'C', 'type': 'in', 'value': ['foo3', 'foo5']}]

    expected = pd.DataFrame({
        'A': np.array([2, 4.]),
        'B': np.array([0, 0.]),
        'C': np.array(['foo3', 'foo5']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=[2, 4])
    pd.testing.assert_frame_equal(
        table._processed, expected if pagination == 'remote' else df
    )

@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_tabulator_constant_single_element_list_filter_client_side(document, comm, pagination):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination=pagination)

    table.filters = [{'field': 'C', 'type': 'in', 'value': ['foo3']}]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'B': np.array([0.]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=[2])
    pd.testing.assert_frame_equal(
        table._processed, expected if pagination == 'remote' else df
    )

@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_tabulator_keywords_filter_client_side(document, comm, pagination):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination=pagination)

    table.filters = [{'field': 'C', 'type': 'keywords', 'value': 'foo3 foo5'}]

    expected = pd.DataFrame({
        'A': np.array([2, 4.]),
        'B': np.array([0, 0.]),
        'C': np.array(['foo3', 'foo5']),
        'D': np.array(['2009-01-05T00:00:00.000000000',
                       '2009-01-07T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=[2, 4])
    pd.testing.assert_frame_equal(
        table._processed, expected if pagination == 'remote' else df
    )

@pytest.mark.parametrize('pagination', ['local', 'remote', None])
def test_tabulator_keywords_match_all_filter_client_side(document, comm, pagination):
    df = makeMixedDataFrame()
    table = Tabulator(
        df,
        header_filters={'C': {'type': 'input', 'func': 'keywords', 'matchAll': True}},
        pagination=pagination
    )

    table.filters = [{'field': 'C', 'type': 'keywords', 'value': 'f oo 3'}]

    expected = pd.DataFrame({
        'A': np.array([2.]),
        'B': np.array([0.]),
        'C': np.array(['foo3']),
        'D': np.array(['2009-01-05T00:00:00.000000000'],
                      dtype='datetime64[ns]')
    }, index=[2])
    pd.testing.assert_frame_equal(
        table._processed, expected if pagination == 'remote' else df
    )

def test_tabulator_constant_scalar_filter_client_side_with_pagination(document, comm):
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

def test_tabulator_constant_scalar_filter_on_index_client_side_with_pagination(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df, pagination='remote')

    model = table.get_root(document, comm)

    table.filters = [{'field': 'index', 'sorter': 'number', 'type': '=', 'value': 2}]

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

def test_tabulator_constant_scalar_filter_on_multi_index_client_side_with_pagination(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df.set_index(['A', 'C']), pagination='remote')

    model = table.get_root(document, comm)

    table.filters = [
        {'field': 'A', 'sorter': 'number', 'type': '=', 'value': 2},
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

def test_tabulator_constant_list_filter_client_side_with_pagination(document, comm):
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

def test_tabulator_keywords_filter_client_side_with_pagination(document, comm):
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

def test_tabulator_keywords_match_all_filter_client_side_with_pagination(document, comm):
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

@pytest.mark.parametrize('col', ['A', 'B', 'C', 'D'])
def test_tabulator_constant_list_filter(document, comm, col):
    df = makeMixedDataFrame()
    # The mixed dataframe has duplicate number values in the B columns,
    # simplify the test by setting the targeted valued before filtering.
    df.at[2, 'B'] = 10.0
    df.at[4, 'B'] = 20.0
    table = Tabulator(df)

    model = table.get_root(document, comm)

    values = list(df.iloc[[2, 4], :][col])

    table.add_filter(values, col)

    expected = {
        'index': np.array([2, 4]),
        'A': np.array([2., 4.]),
        'B': np.array([10., 20.]),
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

def test_tabulator_function_filter_selection(document, comm):
    # issue https://github.com/holoviz/panel/issues/7695
    def generate_random_string(min_length=5, max_length=20):
        length = random.randint(min_length, max_length)
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def df_strings():
        num_strings = 12
        randomized_descr = [generate_random_string() for _ in range(num_strings)]
        code = [f'{i:02d}' for i in range(num_strings)]
        return pd.DataFrame(dict(code=code, descr=randomized_descr))

    df = df_strings()
    tbl = Tabulator(df)

    descr_filter = TextInput(name='descr', value='')

    def contains_filter(df, pattern=None):
        if not pattern:
            return df
        return df[df.descr.str.contains(pattern, case=False)]

    filter_fn = param.bind(contains_filter, pattern=descr_filter)

    tbl.add_filter(filter_fn)

    model = tbl.get_root(document, comm)

    tbl.selection = [0, 1, 2]

    assert model.source.selected.indices == [0, 1, 2]

    descr_filter.value = df.iloc[5, -1]

    assert model.source.selected.indices == []

    descr_filter.value = ""

    assert model.source.selected.indices == [0, 1, 2]


def test_tabulator_function_mask_filter(document, comm):
    df = makeMixedDataFrame()
    table = Tabulator(df)

    model = table.get_root(document, comm)

    widget = TextInput(value='foo3')

    def filter_c(df, value):
        return df.C.str.contains(value)

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

    custom_df = pd.DataFrame({
        'C_l0_g0': {'R_l0_g0': 'R0C0', 'R_l0_g1': 'R1C0'},
        'C_l0_g1': {'R_l0_g0': 'R0C1', 'R_l0_g1': 'R1C1'}
    })
    custom_df.index.name = 'R0'
    custom_df.columns.name = 'C0'
    table.value = custom_df

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

    serve_and_request(table)

    wait_until(lambda: bool(table._models))
    ref, (model, _) = list(table._models.items())[0]
    doc = list(table._documents.keys())[0]

    events = []
    table.on_edit(lambda e: events.append(e))

    new_data = dict(model.source.data)
    new_data['B'][1] = 3.14

    table._server_change(doc, ref, None, 'data', model.source.data, new_data)
    table._server_event(doc, TableEditEvent(model, 'B', 1))

    wait_until(lambda: len(events) == 1)
    assert events[0].value == 3.14
    assert events[0].old == 1


def test_edit_with_datetime_aware_column():
    # https://github.com/holoviz/panel/issues/6673

    # The order of these columns matter, 'B' and 'C' should be first as it's in fact
    # processed first when 'A' is edited.
    data = {
        "B": pd.date_range(start='2024-01-01', end='2024-01-03', freq='D', tz='utc'),
        "C": pd.date_range(start='2024-01-01', end='2024-01-03', freq='D', tz=ZoneInfo('US/Eastern')),
        "A": ['a', 'b', 'c'],
    }
    df = pd.DataFrame(data)

    table = Tabulator(df)

    serve_and_request(table)

    wait_until(lambda: bool(table._models))
    ref, (model, _) = list(table._models.items())[0]
    doc = list(table._documents.keys())[0]

    events = []
    table.on_edit(lambda e: events.append(e))

    new_data = dict(model.source.data)
    new_data['A'][1] = 'new'

    table._server_change(doc, ref, None, 'data', model.source.data, new_data)
    table._server_event(doc, TableEditEvent(model, 'A', 1))

    wait_until(lambda: len(events) == 1)
    assert events[0].value == 'new'
    assert events[0].old == 'b'

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
        count[0] += 1
        counts.append(count[0])
        await asyncio.sleep(1)
        count[0] -= 1

    table.on_click(cb)

    serve_and_request(table)

    wait_until(lambda: bool(table._models))
    doc = list(table._models.values())[0][0].document

    data = df.reset_index()
    with set_curdoc(doc):
        for col in data.columns:
            for row in range(len(data)):
                event = CellClickEvent(model=None, column=col, row=row)
                table._process_event(event)

    # Ensure multiple callbacks started concurrently
    wait_until(lambda: len(counts) >= 1 and max(counts) > 1)

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

def test_tabulator_pagination_remote_cell_click_event_with_stream():
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
            table.stream(pd.DataFrame([(5.0, 0, 'foo6', df.D.iloc[-1])], columns=df.columns, index=[5]))

def test_tabulator_cell_click_event_error_duplicate_index():
    df = pd.DataFrame(data={'A': [1, 2]}, index=['a', 'a'])
    table = Tabulator(df, sorters=[{'field': 'A', 'sorter': 'number', 'dir': 'desc'}])

    values = []
    table.on_click(lambda e: values.append((e.column, e.row, e.value)))

    event = CellClickEvent(model=None, column='y', row=0)
    with pytest.raises(ValueError, match="Found this duplicate index: 'a'"):
        table._process_event(event)

def test_tabulator_styling_empty_dataframe(document, comm):
    df = pd.DataFrame(columns=["A", "B", "C"]).astype({
        "A": float,
        "B": str,
        "C": int,
    })
    table = Tabulator(df)
    table.style.apply(lambda x: [
        "border-color: #dc3545; border-style: solid" for name, value in x.items()
    ], axis=1)

    model = table.get_root(document, comm)

    assert model.styles == {}

    table.value = pd.DataFrame({'A': [3.14], 'B': ['foo'], 'C': [3]})

    assert model.cell_styles['data'] == {
        0: {
            2: [('border-color', '#dc3545'), ('border-style', 'solid')],
            3: [('border-color', '#dc3545'), ('border-style', 'solid')],
            4: [('border-color', '#dc3545'), ('border-style', 'solid')]
        }
    }

def test_tabulator_style_multi_index_dataframe(document, comm):
    # See https://github.com/holoviz/panel/issues/6151
    arrays = [['A', 'A', 'B', 'B'], [1, 2, 1, 2]]
    index = pd.MultiIndex.from_arrays(arrays, names=('Letters', 'Numbers'))
    df = pd.DataFrame({
        'Values': [1, 2, 3, 4],
        'X': [10, 20, 30, 40],
        'Y': [100, 200, 300, 400],
        'Z': [1000, 2000, 3000, 4000]
    }, index=index)

    def color_func(vals):
        return ["background-color: #ff0000;" for v in vals]

    tabulator = Tabulator(df, width=500, height=300)
    tabulator.style.apply(color_func, subset = ['X'])

    model = tabulator.get_root(document, comm)

    assert model.cell_styles['data'] == {
        0: {4: [('background-color', '#ff0000')]},
        1: {4: [('background-color', '#ff0000')]},
        2: {4: [('background-color', '#ff0000')]},
        3: {4: [('background-color', '#ff0000')]}
    }


@mpl_available
def test_tabulator_style_background_gradient_with_frozen_columns(document, comm):
    df = pd.DataFrame(np.random.rand(3, 5), columns=list("ABCDE"))
    table = Tabulator(df, frozen_columns=['A'])
    table.style.background_gradient(
        cmap="RdYlGn_r", vmin=0, vmax=0.5, subset=["A", "C", "D"]
    )

    model = table.get_root(document, comm)

    assert list(model.cell_styles['data'][0]) == [1, 4, 5]

@mpl_available
def test_tabulator_style_background_gradient_with_frozen_columns_left_and_right(document, comm):
    df = pd.DataFrame(np.random.rand(3, 5), columns=list("ABCDE"))
    table = Tabulator(df, frozen_columns={'A': 'left', 'C': 'right'})
    table.style.background_gradient(
        cmap="RdYlGn_r", vmin=0, vmax=0.5, subset=["A", "C", "D"]
    )

    model = table.get_root(document, comm)

    assert list(model.cell_styles['data'][0]) == [1, 6, 4]

@mpl_available
def test_tabulator_style_background_with_frozen_index(document, comm):
    df = pd.DataFrame([[1, 2, 3, 4, 5]], columns=list("abcde")).set_index("a")
    table = Tabulator(df, frozen_columns=["a"])
    table.style.background_gradient(vmin=0, vmax=1, subset=["c"])

    model = table.get_root(document, comm)

    assert list(model.cell_styles['data'][0]) == [3]


@mpl_available
def test_tabulator_style_background_with_frozen_indexes(document, comm):
    df = pd.DataFrame([[1, 2, 3, 4, 5]], columns=list("abcde")).set_index(["a", "b"])
    table = Tabulator(df, frozen_columns=["a", "b"])
    table.style.background_gradient(vmin=0, vmax=1, subset=["c"])

    model = table.get_root(document, comm)

    assert list(model.cell_styles['data'][0]) == [3]


@mpl_available
def test_tabulator_style_background_with_frozen_index_and_column(document, comm):
    df = pd.DataFrame([[1, 2, 3, 4, 5]], columns=list("abcde")).set_index(["a", "d"])
    table = Tabulator(df, frozen_columns=["a", "b"])
    table.style.background_gradient(vmin=0, vmax=1, subset=["c"])

    model = table.get_root(document, comm)

    assert list(model.cell_styles['data'][0]) == [4]


@mpl_available
def test_tabulator_style_background_gradient(document, comm):
    df = pd.DataFrame(np.random.rand(3, 5), columns=list("ABCDE"))
    table = Tabulator(df)
    table.style.background_gradient(
        cmap="RdYlGn_r", vmin=0, vmax=0.5, subset=["A", "C", "D"]
    )

    model = table.get_root(document, comm)

    assert list(model.cell_styles['data'][0]) == [2, 4, 5]

@mpl_available
def test_tabulator_styled_df_with_background_gradient(document, comm):
    df = pd.DataFrame(np.random.rand(3, 5), columns=list("ABCDE")).style.background_gradient(
        cmap="RdYlGn_r", vmin=0, vmax=0.5, subset=["A", "C", "D"]
    )
    table = Tabulator(df)

    model = table.get_root(document, comm)

    assert list(model.cell_styles['data'][0]) == [2, 4, 5]

def test_tabulator_editor_property_change(dataframe, document, comm):
    editor = SelectEditor(options=['A', 'B', 'C'])
    table = Tabulator(dataframe, editors={'str': editor})
    model = table.get_root(document, comm)

    model_editor = model.columns[-1].editor
    assert isinstance(model_editor, SelectEditor) is not editor
    assert isinstance(model_editor, SelectEditor)
    assert model_editor.options == editor.options

    editor.options = ['D', 'E']
    model_editor = model.columns[-1].editor
    assert model_editor.options == editor.options

def test_tabulator_formatter_update(dataframe, document, comm):
    formatter = NumberFormatter(format='0.0000')
    table = Tabulator(dataframe, formatters={'float': formatter})
    model = table.get_root(document, comm)
    model_formatter = model.columns[2].formatter
    assert model_formatter is not formatter
    assert isinstance(model_formatter, NumberFormatter)
    assert model_formatter.format == formatter.format

    formatter.format = '0.0'
    model_formatter = model.columns[2].formatter
    assert model_formatter.format == formatter.format

def test_tabulator_sortable_update(dataframe, document, comm):
    table = Tabulator(dataframe, sortable={'int': False})
    model = table.get_root(document, comm)
    assert not model.configuration['columns'][1]['headerSort']

    table.sortable = {'int': True, 'float': False}
    assert model.configuration['columns'][1]['headerSort']
    assert not model.configuration['columns'][2]['headerSort']

def test_tabulator_hidden_columns_fix():
    # Checks for: https://github.com/holoviz/panel/issues/4102
    #             https://github.com/holoviz/panel/issues/5209
    table = Tabulator(pd.DataFrame(), show_index=False)
    table.hidden_columns = ["a", "b", "c"]
    assert table.hidden_columns == ["a", "b", "c"]

@pytest.mark.parametrize('align', [{"x": "right"}, "right"], ids=["dict", "str"])
def test_bokeh_formatter_with_text_align(align):
    # https://github.com/holoviz/panel/issues/5807
    data = pd.DataFrame({"x": [1.1, 2.0, 3.47]})
    formatters = {"x": NumberFormatter(format="0.0")}
    assert formatters["x"].text_align == "left"  # default
    model = Tabulator(data, formatters=formatters, text_align=align)
    columns = model._get_column_definitions("x", data)
    output = columns[0].formatter.text_align
    assert output == "right"

@pytest.mark.parametrize('align', [{"x": "right"}, "right"], ids=["dict", "str"])
def test_bokeh_formatter_with_text_align_conflict(align):
    # https://github.com/holoviz/panel/issues/5807
    data = pd.DataFrame({"x": [1.1, 2.0, 3.47]})
    formatters = {"x": NumberFormatter(format="0.0", text_align="center")}
    model = Tabulator(data, formatters=formatters, text_align=align)
    msg = r"The 'text_align' in Tabulator\.formatters\['x'\] is overridden by Tabulator\.text_align"
    with pytest.warns(RuntimeWarning, match=msg):
        columns = model._get_column_definitions("x", data)
    output = columns[0].formatter.text_align
    assert output == "right"

def test_bokeh_formatter_index_with_no_textalign():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [1, 2, 3]})
    df = df.set_index("A")

    index_format = HTMLTemplateFormatter(
        template='<a href="https://www.google.com/search?code=<%= value %>"><%= value %></a>'
    )

    table = Tabulator(df, formatters={"A": index_format})
    serve_and_request(table)
    wait_until(lambda: bool(table._models))

@pytest.mark.parametrize('text_align', [{"A": "center"}, "center"], ids=["dict", "str"])
def test_bokeh_formatter_column_with_no_textalign_but_text_align_set(document, comm, text_align):
    df = pd.DataFrame({"A": [1, 2, 3]})
    table = Tabulator(
        df,
        formatters=dict(A=HTMLTemplateFormatter(template='<b><%= value %>"></b>')),
        text_align=text_align,
    )

    model = table.get_root(document, comm)
    assert model.configuration['columns'][1]['hozAlign'] == 'center'


def test_selection_cleared_remote_pagination_new_values(document, comm):
    df = pd.DataFrame(range(200))
    table = Tabulator(df, page_size=50, pagination="remote", selectable="checkbox")
    table.selection = [1, 2, 3]

    table.value = df
    assert table.selection == [1, 2, 3]

    table.value = df.copy()
    assert table.selection == []


def test_save_user_columns_configuration(document, comm):
    df = pd.DataFrame({"header": [True, False, True]})
    configuration={"columns": [{"field": "header", "headerTooltip": True}]}
    tabulator = Tabulator(df, configuration=configuration, show_index=False)

    expected = [{'field': 'header', 'sorter': 'boolean', 'headerTooltip': True}]
    model = tabulator.get_root(document, comm)
    assert model.configuration["columns"] == expected

def test_header_filters_categorial_dtype():
    # Test for https://github.com/holoviz/panel/issues/7234
    df = pd.DataFrame({'model': ['A', 'B', 'C', 'D', 'E']})
    df['model'] = df['model'].astype('category')

    widget = Tabulator(df, header_filters=True)
    widget.filters = [{'field': 'model', 'type': 'like', 'value': 'A'}]
    assert widget.current_view.size == 1

@pytest.mark.parametrize('aggs', [{}, {'Country': 'sum'}, {'Country': {'Int': 'sum', 'Float': 'mean'}}])
def test_tabulator_aggregators(document, comm, df_agg, aggs):
    tabulator = Tabulator(df_agg, hierarchical=True, aggregators=aggs)
    tabulator.get_root(document, comm)
