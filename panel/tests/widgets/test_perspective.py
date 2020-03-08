import panel as pn

pn.pane.perspective.extend()
pn.config.sizing_mode="stretch_width"

def test_constructor():
    perspective = pn.pane.Perspective(height=500)

    assert perspective.html.startswith('<perspective-viewer id="view1" class="perspective-viewer-material" style="height:100%;width:100%"></perspective-viewer>')
    return perspective

if __name__.startswith("bk"):
    show_html=True
    perspective = pn.pane.Perspective(height=500)
    def section(component, message=None, show_html=show_html):
        title = "## " + str(type(component)).split(".")[3][:-2]

        parameters = list(component._child_parameters())
        if show_html:
            parameters = ["html"] + parameters

        if message:
            return (title, component, pn.Param(component, parameters=parameters), pn.pane.Markdown(message), pn.layout.Divider())
        return (title, component, pn.Param(component, parameters=parameters), pn.layout.Divider())

    pn.Column(*section(perspective)).servable()