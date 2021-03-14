import panel as pn


def test_constructor():
    chartjs = pn.pane.ChartJS(object="Click Me Now!")

def get_app():
    chartjs = pn.pane.ChartJS(object="Click Me Now!")
    return pn.Column(
        chartjs, pn.Param(chartjs, parameters=["object", "clicks"])
    )

if __name__.startswith("bokeh"):
    pn.config.js_files["chartjs"]="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"
    get_app().servable()