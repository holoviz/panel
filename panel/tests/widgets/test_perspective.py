# pylint: disable=redefined-outer-name,protected-access
# pylint: disable=missing-function-docstring,missing-module-docstring,missing-class-docstring
import random

import pandas as pd
import panel as pn
import pytest
from bokeh.models import ColumnDataSource

from panel.widgets.dataframe_base import DataFrameWithStreamAndPatchBaseWidget
from panel.widgets.perspective_viewer import PerspectiveViewer


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
    assert issubclass(PerspectiveViewer, DataFrameWithStreamAndPatchBaseWidget)


def test_constructor(dataframe):
    # When
    component = PerspectiveViewer(value=dataframe)

    # Then
    assert component.theme == "material"
    assert component.value is dataframe
    assert component.plugin == "datagrid"
    assert component.columns is None
    assert component.computed_columns is None
    assert component.column_pivots is None
    assert component.row_pivots is None
    assert component.aggregates is None
    assert component.sort is None
    assert component.filters is None

    assert isinstance(component._source, ColumnDataSource)
    pd.testing.assert_frame_equal(component._source.to_df(), dataframe.reset_index())


def test_perspective_comms(document, comm, dataframe):
    # Given
    perspective = PerspectiveViewer(value=dataframe)
    widget = perspective.get_root(document, comm=comm)

    # Then
    assert isinstance(widget, perspective._widget_type)
    assert widget.source == perspective._source

    # # When
    # with param.edit_constant(tabulator):
    #     tabulator._process_events(
    #         {"configuration": {"a": 1},}
    #     )

    # # Then
    # assert tabulator.configuration == {"a": 1}


def test_example_app():
    data = [
        {"x": 1, "y": "a", "z": True},
        {"x": 2, "y": "b", "z": False},
        {"x": 3, "y": "c", "z": True},
        {"x": 4, "y": "d", "z": False},
    ]
    dataframe = pd.DataFrame(data)
    perspective = PerspectiveViewer(
        height=500,
        value=dataframe.copy(deep=True),
        columns=["index", "x", None, None, None],
        plugin="d3_xy_scatter",
    )

    def stream(*_):
        new_index = perspective.value.index.max()
        new_data = {"x": [random.uniform(-3, new_index)], "y": ["e"], "z": [True]}
        new_series = pd.DataFrame(data=new_data)
        perspective.stream(new_series)

    stream_button = pn.widgets.Button(name="STREAM", button_type="success")
    stream_button.on_click(stream)

    def patch(*_):
        new_value = perspective.value.copy(deep=True)
        new_value["x"] = new_value["x"] - 1
        new_value["z"] = ~new_value["z"]
        perspective.patch(new_value)

    patch_button = pn.widgets.Button(name="PATCH", button_type="default")
    patch_button.on_click(patch)

    def reset(*_):
        perspective.value = dataframe.copy(deep=True)

    reset_button = pn.widgets.Button(name="RESET", button_type="default")
    reset_button.on_click(reset)

    def section(component, message=None):
        title = "## " + str(type(component)).split(".")[-1][:-2]

        parameters = [
            "value",
            "columns",
            # "parsed_computed_columns",
            "computed_columns",
            "column_pivots",
            "row_pivots",
            "aggregates",
            "sort",
            "filters",
            "plugin",
            "theme",
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
            pn.Row(stream_button, patch_button, reset_button),
            # pn.Param(component, parameters=parameters),
            pn.layout.Divider(),
        )

    return pn.Column(*section(perspective), width=800, sizing_mode="stretch_height")


def test_reference_notebook_example():
    DARK_BACKGROUND = "rgb(42, 44, 47)"  # pylint: disable=invalid-name
    PERSPECTIVE_LOGO = "https://perspective.finos.org/img/logo.png"  # pylint: disable=invalid-name
    top_app_bar = pn.Row(
        pn.pane.PNG(PERSPECTIVE_LOGO, height=50, margin=(10, 25, 10, 10)),
        pn.layout.HSpacer(),
        margin=0,
        background=DARK_BACKGROUND,
    )
    # pn.config.sizing_mode = "stretch_width"
    data = [
        {"x": 1, "y": "a", "z": True},
        {"x": 2, "y": "b", "z": False},
        {"x": 3, "y": "c", "z": True},
        {"x": 4, "y": "d", "z": False},
    ]
    dataframe = pd.DataFrame(data)
    perspective = PerspectiveViewer(
        height=500,
        value=dataframe.copy(deep=True),
        columns=["index", "x", None, None, None],
        plugin="d3_xy_scatter",
        sizing_mode="stretch_width",
    )

    def stream(*_):
        new_index = perspective.value.index.max()
        new_data = {"x": [random.uniform(-3, new_index)], "y": ["e"], "z": [True]}
        new_series = pd.DataFrame(data=new_data)
        perspective.stream(new_series)

    stream_button = pn.widgets.Button(name="STREAM", button_type="success")
    stream_button.on_click(stream)

    def patch(*_):
        new_value = perspective.value.copy(deep=True)
        new_value["x"] = new_value["x"] - 1
        new_value["z"] = ~new_value["z"]
        perspective.patch(new_value)

    patch_button = pn.widgets.Button(name="PATCH", button_type="default")
    patch_button.on_click(patch)

    def reset(*_):
        perspective.value = dataframe.copy(deep=True)

    reset_button = pn.widgets.Button(name="RESET", button_type="default")
    reset_button.on_click(reset)

    return pn.Column(
        top_app_bar,
        pn.Row(
            perspective,
            pn.WidgetBox(stream_button, patch_button, reset_button),
            sizing_mode="stretch_width",
        ),
        perspective.param.value,
        sizing_mode="stretch_width",
    )


if __name__.startswith("bokeh"):
    test_reference_notebook_example().servable()
elif __name__ == "__main__":
    test_reference_notebook_example().show(port=5007)
