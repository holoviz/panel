# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring

import pandas as pd
import panel as pn
import pytest
from bokeh.models import ColumnDataSource

from panel.widgets.dataframe_base import DataFrameWithStreamAndPatchBaseWidget
from panel.widgets.pivot_table import PivotTable


@pytest.fixture
def data():
    return {"x": [1, 2, 3, 4], "y": ["a", "b", "c", "d"], "z": [True, False, True, False]}


@pytest.fixture
def dataframe(data):
    return pd.DataFrame(data)


def test_is_dataframe_base_widget():
    """A lot of the functionality comes by inheriting from
    DataFrameWithStreamAndPatchBaseWidget. If that is changed we would need to add or change some
    testing here"""
    assert issubclass(PivotTable, DataFrameWithStreamAndPatchBaseWidget)


def test_constructor(dataframe):
    # When
    component = PivotTable(value=dataframe)

    # Then
    assert component.height > 0

    assert isinstance(component._source, ColumnDataSource)
    pd.testing.assert_frame_equal(component._source.to_df(), dataframe.reset_index())


def test_pivot_table_comms(document, comm, dataframe):
    # Given
    pivot_table = PivotTable(value=dataframe)
    widget = pivot_table.get_root(document, comm=comm)

    # Then
    assert isinstance(widget, pivot_table._widget_type)
    assert widget.source == pivot_table._source


def test_example_app():
    data = [
        {"x": 1, "y": "a", "z": True},
        {"x": 2, "y": "b", "z": False},
        {"x": 3, "y": "c", "z": True},
        {"x": 4, "y": "d", "z": False},
    ]
    dataframe = pd.DataFrame(data)
    pivot_table = PivotTable(
        height=500,
        value=dataframe.copy(deep=True),
        columns=["index", "x", None, None, None],
        plugin="d3_xy_scatter",
    )

    def section(component, message=None):
        title = "## " + str(type(component)).split(".")[-1][:-2]

        parameters = [
            "value",
            # "columns",
            # # "parsed_computed_columns",
            # "computed_columns",
            # "column_pivots",
            # "row_pivots",
            # "aggregates",
            # "sort",
            # "filters",
            # "plugin",
            # "theme",
        ]

        if message:
            return (
                pn.pane.Markdown(title),
                component,
                pn.Param(component, parameters=parameters),
                pn.pane.Markdown(message),
                pn.layout.Divider(),
            )
        return (
            pn.pane.Markdown(title),
            component,
            # pn.Param(component, parameters=parameters),
            pn.layout.Divider(),
        )

    return pn.Column(*section(pivot_table), width=800, sizing_mode="stretch_height")


def test_reference_notebook_example():
    DARK_BACKGROUND = "rgb(42, 44, 47)"  # pylint: disable=invalid-name
    top_app_bar = pn.Row(
        pn.pane.HTML("<h1 style='color:white'>PivotTable.js</h1>"),
        pn.layout.HSpacer(),
        margin=0,
        background=DARK_BACKGROUND,
    )
    # pn.config.sizing_mode = "stretch_width"
    # Source: https://datahub.io/core/s-and-p-500-companies-financials
    data = (
        "https://raw.githubusercontent.com/MarcSkovMadsen/awesome-panel/master/application/"
        "pages/awesome_panel_express_tests/PerspectiveViewerData.csv"
    )
    dataframe = pd.read_csv(data)
    columns = [
        "Name",
        "Symbol",
        "Sector",
        "Price",
        "52 Week Low",
        "52 Week High",
        "Price/Earnings",
        "Price/Sales",
        "Price/Book",
        "Dividend Yield",
        "Earnings/Share",
        "Market Cap",
        "EBITDA",
        "SEC Filings",
    ]
    dataframe = dataframe[columns]
    pivot_table = PivotTable(
        height=500, value=dataframe.copy(deep=True), sizing_mode="stretch_width",
    )
    return pn.Column(
        top_app_bar, pn.Row(pivot_table, sizing_mode="stretch_width",), sizing_mode="stretch_width",
    )


if __name__.startswith("bokeh"):
    test_reference_notebook_example().servable()
