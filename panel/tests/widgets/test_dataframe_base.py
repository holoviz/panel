# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
# pylint: disable=global-statement
import pandas as pd
import param
import pytest
from bokeh.models.sources import ColumnDataSource

from panel.widgets.dataframe_base import (
    DataFrameWithStreamAndPatchBaseWidget as DFWidget,
)

VALUE_CHANGED_COUNT = 0

# region value


@pytest.fixture
def data():
    return {"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"], "z": [True, False, True, False]}


@pytest.fixture
def dataframe(data):
    return pd.DataFrame(data)


def test_constructor(dataframe):
    # When
    component = DFWidget(value=dataframe)

    # Then
    assert component.value is dataframe
    assert isinstance(component._source, ColumnDataSource)
    pd.testing.assert_frame_equal(component._source.to_df(), dataframe.reset_index())


def test_constructor_no_value():
    # When
    component = DFWidget()
    # Then
    assert isinstance(component._source, ColumnDataSource)


def test_change_value(dataframe):
    # Given
    component = DFWidget()
    # When
    component.value = dataframe
    # Then
    pd.testing.assert_frame_equal(component._source.to_df(), dataframe.reset_index())


# endregion value

# region stream


def test_stream_dataframe_dataframe_value():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = DFWidget(value=value)
    stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*_):
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
    tabulator = DFWidget(value=value)
    stream_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]}).loc[1]

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*_):
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
    tabulator = DFWidget(value=value)
    stream_value = {"x": [3, 4], "y": ["c", "d"]}

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*_):
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
    tabulator = DFWidget(value=value)
    stream_value = {"x": 4, "y": "d"}

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*_):
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


# endregion Stream

# region Patch


def test_patch_dataframe_dataframe_value():
    # Given
    value = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    tabulator = DFWidget(value=value)
    patch_value = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})

    # Used to test that value event is triggered
    global VALUE_CHANGED_COUNT
    VALUE_CHANGED_COUNT = 0

    @param.depends(tabulator.param.value, watch=True)
    def _inc(*_):
        global VALUE_CHANGED_COUNT
        VALUE_CHANGED_COUNT += 1

    # When
    tabulator.patch(patch_value)
    # Then
    tabulator_source_df = tabulator._source.to_df().drop(columns=["index"])
    expected = pd.DataFrame({"x": [3, 4], "y": ["c", "d"]})
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
    tabulator = DFWidget(value=data1)
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
    with pytest.raises(ValueError) as error:
        DFWidget(value=data2)

    assert str(error.value) == (
        "Please provide a DataFrame with RangeIndex starting at 0 and with step 1"
    )


def test_patch_and_reset():
    """I experienced some strange behaviour which I test below.

    The code actually worked as it should. The problem was that I patched the original
    data so I could never "reset" back to the original data
    """
    # Given
    data = pd.DataFrame({"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"]})
    data_copy = data.copy(deep=True)
    tabulator = DFWidget(value=data_copy)
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
    tabulator = DFWidget(value=data1)
    # When replace, stream and reset
    tabulator.value = data2
    tabulator.stream(stream_value=data3)
    tabulator.value = data.copy(deep=True).loc[
        0:1,
    ]
    # Then
    assert set(tabulator._source.data["x"]) == {1, 2}
