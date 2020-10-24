# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
"""This module contains tests of the tabulator Data Grid"""

# http://tabulator.info/docs/4.7/quickstart
# https://github.com/paulhodel/jexcel


import pandas as pd
import panel as pn
import param
import pytest
from _pytest._code.code import TerminalRepr
from bokeh.models import ColumnDataSource

from panel.widgets.tabulator import TABULATOR_CSS_THEMES, Tabulator


def _data_records():
    return [
        {"id": 1, "name": "Oli Bob", "age": 12, "col": "red", "dob": pd.Timestamp("14/05/1982")},
        {"id": 2, "name": "Mary May", "age": 1, "col": "blue", "dob": pd.Timestamp("14/05/1982")},
        {
            "id": 3,
            "name": "Christine Lobowski",
            "age": 42,
            "col": "green",
            "dob": pd.Timestamp("22/05/1982"),
        },
        {
            "id": 4,
            "name": "Brendon Philips",
            "age": 125,
            "col": "orange",
            "dob": pd.Timestamp("01/08/1980"),
        },
        {
            "id": 5,
            "name": "Margret Marmajuke",
            "age": 16,
            "col": "yellow",
            "dob": pd.Timestamp("31/01/1999"),
        },
    ]


@pytest.fixture()
def data_records():
    return _data_records()


@pytest.fixture()
def dataframe(data_records):
    return pd.DataFrame(data=data_records)


@pytest.fixture()
def data_list(dataframe):
    return dataframe.to_dict("list")


@pytest.fixture()
def column_data_source(data_list):
    return ColumnDataSource(data_list)


@pytest.fixture()
def columns():
    return [
        {
            "title": "Id",
            "field": "id",
            "sorter": "number",
            "formatter": "money",
            "hozAlign": "right",
        },
        {
            "title": "Name",
            "field": "name",
            "sorter": "string",
            "formatter": "plaintext",
            "hozAlign": "left",
        },
        {
            "title": "Age",
            "field": "age",
            "sorter": "number",
            "formatter": "money",
            "hozAlign": "right",
        },
        {
            "title": "Col",
            "field": "col",
            "sorter": "string",
            "formatter": "plaintext",
            "hozAlign": "left",
        },
        {
            "title": "Dob",
            "field": "dob",
            "sorter": "datetime",
            "formatter": "datetime",
            "hozAlign": "left",
        },
    ]


@pytest.fixture()
def configuration():
    # http://tabulator.info/docs/4.7/quickstart
    return {"autoColumns": True}


@pytest.fixture
def tabulator(configuration, dataframe):
    return Tabulator(configuration=configuration, value=dataframe)


def test_constructor():
    # When
    tabulator = Tabulator()
    # Then
    assert not tabulator.value
    assert isinstance(tabulator._source, ColumnDataSource)
    assert tabulator.configuration == {"autoColumns": True}
    assert tabulator.selection == []
    assert tabulator.selected_values is None


def test_tabulator_from_dataframe(dataframe, configuration):
    tabulator = Tabulator(value=dataframe, configuration=configuration)
    assert isinstance(tabulator._source, ColumnDataSource)


def test_tabulator_from_column_data_source(column_data_source, configuration):
    tabulator = Tabulator(value=column_data_source, configuration=configuration)
    assert tabulator._source == tabulator.value


def test_dataframe_to_columns_configuration(dataframe, columns):
    # Given
    value = dataframe
    # When
    actual = Tabulator.to_columns_configuration(value)
    # Then
    assert actual == columns


def test_config_default():
    # When
    Tabulator.config()
    # Then
    assert TABULATOR_CSS_THEMES["default"] in pn.config.css_files


def test_config_none():
    # Given
    css_count = len(pn.config.css_files)
    pn.config.js_files.clear()
    # When
    Tabulator.config(css=None)
    # Then
    assert len(pn.config.css_files) == css_count


def test_config_custom():
    # When
    Tabulator.config(css="materialize")
    # Then
    assert TABULATOR_CSS_THEMES["materialize"] in pn.config.css_files


def test_selection_dataframe(data_records, dataframe):
    # Given
    tabulator = Tabulator(value=dataframe)
    # When
    tabulator.selection = [0, 1, 2]
    actual = tabulator.selected_values
    # Then
    expected = pd.DataFrame(data=data_records[0:3])
    pd.testing.assert_frame_equal(actual, expected)


def test_selection_column_data_source(data_records, column_data_source):
    # Given
    tabulator = Tabulator(value=column_data_source)
    # When
    tabulator.selection = [0, 1, 2]
    actual = tabulator.selected_values
    # Then
    # I could not find a more direct way to test this.
    expected_as_df = pd.DataFrame(data=data_records[0:3])
    pd.testing.assert_frame_equal(actual.to_df().drop(columns="index"), expected_as_df)


@pytest.mark.parametrize(
    ["field", "expected"],
    [("name", "Name"), ("cheese cake", "Cheese Cake"), ("cheese_cake", "Cheese Cake"),],
)
def test_to_title(field, expected):
    assert Tabulator._to_title(field) == expected


def test_tabulator_comms(document, comm, column_data_source, configuration):
    # Given
    tabulator = Tabulator(value=column_data_source, configuration=configuration)
    widget = tabulator.get_root(document, comm=comm)

    # Then
    assert isinstance(widget, tabulator._widget_type)
    assert widget.source == column_data_source
    assert widget.configuration == configuration

    # When
    with param.edit_constant(tabulator):
        tabulator._process_events(
            {"configuration": {"a": 1},}
        )

    # Then
    assert tabulator.configuration == {"a": 1}


def test_selected_change(tabulator):
    # When
    tabulator.selection = [2, 4, 6]
    # Then
    assert tabulator._source.selected.indices == [2, 4, 6]


def test_source_selection_change(tabulator):
    # When
    tabulator._process_events({"indices": [2, 4, 6]})
    # Then
    assert tabulator.selection == [2, 4, 6]


def test_cell_change_when_dataframe():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = Tabulator(value=value)
    original_data = tabulator._source.data
    # When
    tabulator._cell_change = {"c": "x", "i": 1, "v": 3}
    # Then
    assert tabulator.value.loc[1, "x"] == 3
    # And the tabulator._source.data shall not have been updated
    # We currently use the _pause_cds_updates parameter to avoid reupdating the _source.data
    assert tabulator._source.data is original_data


def test_cell_change_when_column_data_source():
    # Given
    value = ColumnDataSource(pd.DataFrame({"x": [1, 2], "y": ["a", "b"]}))
    tabulator = Tabulator(value=value)
    # When
    tabulator._cell_change = {"c": "x", "i": 1, "v": 3}
    # Then we assume the columndatasource has been update on the js side
    # and therefore don't update on the python side
    assert tabulator.value.to_df().loc[1, "x"] == 2


# region stream

VALUE_CHANGED_COUNT = 0


def test_stream_dataframe_dataframe_value():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = Tabulator(value=value)
    stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*events):
        global VALUE_CHANGED_COUNT
        VALUE_CHANGED_COUNT += 1

    # When
    tabulator.stream(stream_value)
    # Then
    tabulator_source_df = tabulator._source.to_df().drop(columns=["index"])
    expected = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})
    pd.testing.assert_frame_equal(tabulator.value, expected)
    pd.testing.assert_frame_equal(tabulator_source_df, expected)
    assert VALUE_CHANGED_COUNT == 1


def test_stream_dataframe_series_value():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = Tabulator(value=value)
    stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]}).loc[1]

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*events):
        global VALUE_CHANGED_COUNT
        VALUE_CHANGED_COUNT += 1

    # When
    tabulator.stream(stream_value)
    # Then
    tabulator_source_df = tabulator._source.to_df().drop(columns=["index"])
    expected = pd.DataFrame({"x": [1, 2, 4], "y": ["a", "b", "d"]})
    pd.testing.assert_frame_equal(tabulator.value, expected)
    pd.testing.assert_frame_equal(
        tabulator_source_df, expected, check_column_type=False, check_dtype=False
    )
    assert VALUE_CHANGED_COUNT == 1


def test_stream_dataframe_dictionary_value_multi():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = Tabulator(value=value)
    stream_value = {"x": [3, 4], "y": ["c", "d"]}

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*events):
        global VALUE_CHANGED_COUNT
        VALUE_CHANGED_COUNT += 1

    # When PROVIDING A DICTIONARY OF COLUMNS
    tabulator.stream(stream_value)
    # Then
    tabulator_source_df = tabulator._source.to_df().drop(columns=["index"])
    expected = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})
    pd.testing.assert_frame_equal(tabulator.value, expected)
    pd.testing.assert_frame_equal(
        tabulator_source_df, expected, check_column_type=False, check_dtype=False
    )
    assert VALUE_CHANGED_COUNT == 1


def test_stream_dataframe_dictionary_value_single():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = Tabulator(value=value)
    stream_value = {"x": 4, "y": "d"}

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*events):
        global VALUE_CHANGED_COUNT
        VALUE_CHANGED_COUNT += 1

    # When PROVIDING A DICTIONARY ROW
    tabulator.stream(stream_value)
    # Then
    tabulator_source_df = tabulator._source.to_df().drop(columns=["index"])
    expected = pd.DataFrame({"x": [1, 2, 4], "y": ["a", "b", "d"]})
    pd.testing.assert_frame_equal(tabulator.value, expected)
    pd.testing.assert_frame_equal(
        tabulator_source_df, expected, check_column_type=False, check_dtype=False
    )
    assert VALUE_CHANGED_COUNT == 1


def test_stream_cds_dictionary_value():
    # Given
    value = ColumnDataSource({"x": [1, 2], "y": ["a", "b"]})
    tabulator = Tabulator(value=value)
    stream_value = {"x": [3, 4], "y": ["c", "d"]}

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*events):
        global VALUE_CHANGED_COUNT
        VALUE_CHANGED_COUNT += 1

    # When
    tabulator.stream(stream_value)
    # Then
    tabulator_source_json = tabulator._source.to_json(include_defaults=False)["data"]
    expected = {"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]}
    assert tabulator.value is value
    assert tabulator_source_json == expected
    assert VALUE_CHANGED_COUNT == 1


# endregion Stream

# region Patch


def test_stream_dataframe_dataframe_value():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = Tabulator(value=value)
    stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*events):
        global VALUE_CHANGED_COUNT
        VALUE_CHANGED_COUNT += 1

    # When
    tabulator.stream(stream_value)
    # Then
    tabulator_source_df = tabulator._source.to_df().drop(columns=["index"])
    expected = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})
    pd.testing.assert_frame_equal(tabulator.value, expected)
    pd.testing.assert_frame_equal(tabulator_source_df, expected)
    assert VALUE_CHANGED_COUNT == 1


# endregion Patch


def test_patch_from_partial_dataframe():
    data = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})
    data1 = data.loc[
        0:1,
    ]
    data2 = data.loc[2:4]
    # When
    tabulator = Tabulator(value=data1)
    tabulator.value = data2.reset_index(drop=True)
    patch_value = tabulator.value["x"] + 2
    tabulator.patch(patch_value)
    # Then
    expected = pd.DataFrame({"x": [5, 6], "y": ["c", "d"]})
    pd.testing.assert_frame_equal(tabulator.value, expected)


def test_range_index_of_dataframe_value():
    # Given
    data = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})
    data2 = data.loc[2:4]
    # When
    with pytest.raises(ValueError) as e:
        Tabulator(value=data2)

    assert (
        str(e.value) == "Please provide a DataFrame with RangeIndex starting at 0 and with step 1"
    )


def test_patch_and_reset():
    """I experienced some strange behaviour which I test below.

    The code actually worked as it should. The problem was that I patched the original
    data so I could never "reset" back to the original data
    """
    # Given
    data = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})
    data_copy = data.copy(deep=True)
    tabulator = Tabulator(value=data_copy)
    patch = tabulator.value["x"] + 2

    # When patch Then
    tabulator.patch(patch_value=patch)
    assert set(tabulator._source.data["x"]) == {3, 4, 5, 6}

    # When reset Then
    tabulator.value = data
    assert set(tabulator._source.data["x"]) == {1, 2, 3, 4}


def test_replace_stream_and_reset():
    # Given
    data = pd.DataFrame({"x": [1, 2, 3, 4, 5], "y": ["a", "b", "c", "d", "e"]})
    data1 = data.copy(deep=True).loc[0:1,].reset_index(drop=True)
    data2 = data.copy(deep=True).loc[2:3,].reset_index(drop=True)
    data3 = data.copy(deep=True).loc[
        4:4,
    ]
    tabulator = Tabulator(value=data1)
    # When replace, stream and reset
    tabulator.value = data2
    tabulator.stream(stream_value=data3)
    tabulator.value = data.copy(deep=True).loc[
        0:1,
    ]
    # Then
    assert set(tabulator._source.data["x"]) == {1, 2}
