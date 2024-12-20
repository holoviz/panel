import panel as pn


def test_constructor():
    pn.pane.ChartJS(object="Click Me Now!")

def get_app():
    chartjs = pn.pane.ChartJS(object="Click Me Now!", )
    return pn.Column(
        chartjs, pn.Param(chartjs, parameters=["object", "clicks"])
    )

if __name__.startswith("bokeh"):
    get_app().servable()
