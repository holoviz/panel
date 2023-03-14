from panel.layout import Row
from panel.pane import ECharts, Markdown

ECHART = {
    "xAxis": {
        "type": 'category',
        "data": ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    },
    "yAxis": {
        "type": 'value'
    },
    "series": [{
        "data": [820, 932, 901, 934, 1290, 1330, 1320],
        "type": 'line'
    }]
}

def test_echart(document, comm):
    echart = ECharts(ECHART, width=500, height=500)
    model = echart.get_root(document, comm)
    assert model.data == ECHART

def test_echart_event(document, comm):
    echart = ECharts(ECHART, width=500, height=500)
    echart.on_event('click', print)
    model = echart.get_root(document, comm)

    assert model.data == ECHART
    assert model.event_config == {'click': [None]}

def test_echart_event_query(document, comm):
    echart = ECharts(ECHART, width=500, height=500)
    echart.on_event('click', print, 'series.line')
    model = echart.get_root(document, comm)
    assert model.data == ECHART
    assert model.event_config == {'click': ['series.line']}

def test_echart_js_event(document, comm):
    echart = ECharts(ECHART, width=500, height=500)
    echart.js_on_event('click', 'console.log(cb_data)')
    model = echart.get_root(document, comm)
    assert model.data == ECHART
    assert 'click' in model.js_events
    assert len(model.js_events['click']) == 1
    assert model.js_events['click'][0]['callback'].code == 'console.log(cb_data)'

def test_echart_js_event_with_arg(document, comm):
    echart = ECharts(ECHART, width=500, height=500)
    md = Markdown()
    echart.js_on_event('click', 'console.log(cb_data)', md=md)
    root = Row(echart, md).get_root(document, comm)
    ref = root.ref['id']
    model = echart._models[ref][0]
    assert model.data == ECHART
    assert 'click' in model.js_events
    assert len(model.js_events['click']) == 1
    handler = model.js_events['click'][0]
    assert handler['callback'].code == 'console.log(cb_data)'
    assert handler['callback'].args == {'md': md._models[ref][0]}
