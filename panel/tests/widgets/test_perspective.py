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
    model = component.get_root(document, comm=comm)

    assert component.html.startswith(
        '<perspective-viewer id="view1" class="perspective-viewer-material-dark" style="height:100%;width:100%" plugin="hypergrid"></perspective-viewer>'
    )
    assert component._models[model.ref["id"]][0] is model
    assert type(model).__name__ == "WebComponent"
    assert isinstance(model.columnDataSource, ColumnDataSource)


if __name__.startswith("bk"):
    show_html = True
    data = [
        {"x": 1, "y": "a", "z": True},
        {"x": 2, "y": "b", "z": False},
        {"x": 3, "y": "c", "z": True},
        {"x": 4, "y": "d", "z": False},
    ]
    dataframe = pd.DataFrame(data)
    perspective = pn.pane.Perspective(height=500, data=dataframe, data_last_change=dataframe)

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
