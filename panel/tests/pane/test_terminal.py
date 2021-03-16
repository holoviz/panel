import panel as pn


def test_constructor():
    terminal = pn.pane.Terminal(object="Click Me Now!")

def get_app():
    terminal = pn.pane.Terminal(object="Click Me Now!")
    return pn.Column(
        terminal, pn.Param(terminal, parameters=["object", "clicks"])
    )

if __name__.startswith("bokeh"):
    get_app().servable()