from __future__ import absolute_import, division, unicode_literals

import pytest

try:
    import pandas as pd
    from pandas.util.testing import makeTimeDataFrame
except ImportError:
    pytestmark = pytest.mark.skip('pandas not available')

from bokeh.models.widgets.tables import (
    NumberFormatter, IntEditor, NumberEditor, StringFormatter,
    SelectEditor, DateFormatter, DataCube, CellEditor,
    SumAggregator, AvgAggregator, MinAggregator
)

from panel.widgets import DataFrame


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

    assert model.columns[-1].editor is editor

    
def test_dataframe_formatter(dataframe, document, comm):
    formatter = NumberFormatter(format='0.0000')
    table = DataFrame(dataframe, formatters={'float': formatter})
    model = table.get_root(document, comm)
    assert model.columns[2].formatter is formatter


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
    print(grouping)
    assert agg1.field_ == 'Int'
    assert isinstance(agg1, MinAggregator)
    assert agg2.field_ == 'Float'
    assert isinstance(agg2, MinAggregator)


def test_none_table(document, comm):
    table = DataFrame(value=None)
    assert table.indexes == []

    model = table.get_root(document, comm)

    assert model.source.data == {}
