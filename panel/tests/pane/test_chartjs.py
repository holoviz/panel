import panel as pn

CHARTJS_CONFIG = {
    'type': 'line',
    'data': {
        'labels': ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
        'datasets': [{
            'label': 'My First dataset',
            'backgroundColor': 'rgb(255, 99, 132)',
            'borderColor': 'rgb(255, 99, 132)',
            'data': [0, 10, 5, 2, 20, 30, 45]
        }]
    },
    'options': {
        'responsive': True,
        'maintainAspectRatio': False,
    }
}

def test_constructor():
    chartjs = pn.pane.ChartJS(object=CHARTJS_CONFIG)

def get_app():
    chartjs = pn.pane.ChartJS(object=CHARTJS_CONFIG)
    return pn.Column(
        chartjs, pn.Param(chartjs, parameters=["object"])
    )

if __name__.startswith("bokeh"):
    pn.config.js_files["chartjs"]="https://cdn.jsdelivr.net/npm/chart.js@2.8.0"
    get_app().servable()