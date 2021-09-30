import re

from io import StringIO

from panel.pane import Alert, Vega
from panel.models.vega import VegaPlot


vega_example = {
    'config': {
        'mark': {'tooltip': None},
        'view': {'height': 300, 'width': 400}
    },
    'data': {'values': [{'x': 'A', 'y': 5},
                        {'x': 'B', 'y': 3},
                        {'x': 'C', 'y': 6},
                        {'x': 'D', 'y': 7},
                        {'x': 'E', 'y': 2}]},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json'
}


def test_save_external():
    sio = StringIO()
    pane = Vega(vega_example)

    pane.save(sio)
    sio.seek(0)
    html = sio.read()
    for js in VegaPlot.__javascript_raw__:
        assert js in html


def test_save_inline_resources():
    alert = Alert('# Save test')

    sio = StringIO()
    alert.save(sio, resources='inline')
    sio.seek(0)
    html = sio.read()
    assert '.bk.alert-primary' in html


def test_save_cdn_resources():
    alert = Alert('# Save test')

    sio = StringIO()
    alert.save(sio, resources='cdn')
    sio.seek(0)
    html = sio.read()
    assert re.findall('https://unpkg.com/@holoviz/panel@(.*)/dist/css/alerts.css', html)
