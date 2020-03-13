import panel as pn

pn.pane.perspective.extend()
pn.config.sizing_mode = "stretch_width"
import pandas as pd
from bokeh.models import ColumnDataSource


def test_constructor(document, comm):
    # Given
    data = [
        {"x": 1, "y": "a", "z": True},
        {"x": 2, "y": "b", "z": False},
        {"x": 3, "y": "c", "z": True},
        {"x": 4, "y": "d", "z": False},
    ]
    dataframe = pd.DataFrame(data)
    component = pn.pane.Perspective(data=dataframe)

    assert component.html.startswith(
        '<perspective-viewer id="view1" class="perspective-viewer-material-dark" style="height:100%;width:100%"'
    )
    assert component.data is dataframe
    assert component.column_data_source_orient == "records"
    assert component.column_data_source_load_function == "load"

    model = component.get_root(document, comm=comm)
    assert component._models[model.ref["id"]][0] is model
    assert type(model).__name__ == "WebComponent"
    assert isinstance(model.columnDataSource, ColumnDataSource)
    assert model.columnDataSourceOrient == "records"
    assert model.columnDataSourceLoadFunction == "load"


if __name__.startswith("bk"):
    show_html = True
    data = [
        {"x": 1, "y": "a", "z": True},
        {"x": 2, "y": "b", "z": False},
        {"x": 3, "y": "c", "z": True},
        {"x": 4, "y": "d", "z": False},
    ]
    dataframe = pd.DataFrame(data)
    perspective = pn.pane.Perspective(height=500, data=dataframe)

    def section(component, message=None, show_html=show_html):
        title = "## " + str(type(component)).split(".")[3][:-2]

        parameters = list(component._child_parameters())
        if show_html:
            parameters = ["html"] + parameters

        if message:
            return (
                title,
                component,
                pn.Param(component, parameters=parameters),
                pn.pane.Markdown(message),
                pn.layout.Divider(),
            )
        return (title, component, pn.Param(component, parameters=parameters), pn.layout.Divider())

    pn.Column(*section(perspective)).servable()
