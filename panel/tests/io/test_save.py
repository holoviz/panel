import re

from io import StringIO
from pathlib import Path

import numpy as np

from bokeh.resources import Resources

from panel.pane import Alert, Vega
from panel.models.vega import VegaPlot
from panel.tests.util import hv_available


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


@hv_available
def test_static_path_in_holoviews_save(tmpdir):
    import holoviews as hv
    hv.Store.set_current_backend('bokeh')
    plot = hv.Curve(np.random.seed(42))
    res = Resources(mode='server', root_url='/')
    out_file = Path(tmpdir) / 'plot.html'
    hv.save(plot, out_file, resources=res)
    content = out_file.read_text()

    assert 'src="/static/js/bokeh' in content and 'src="static/js/bokeh' not in content
    assert 'href="/static/extensions/panel/css/' in content and 'href="static/extensions/panel/css/' not in content
