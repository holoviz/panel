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

MINIMAL_GEOJSON = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"name": "TestRegion"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
        }
    }]
}


def test_echart_geo_data(document, comm):
    echart_config = {
        "geo": {"map": "test"},
        "series": [],
    }
    echart = ECharts(echart_config, geo_data={"test": MINIMAL_GEOJSON},
                     width=500, height=500)
    model = echart.get_root(document, comm)
    assert model.data == echart_config
    assert model.geo_data == {"test": MINIMAL_GEOJSON}


def test_echart_geo_data_default(document, comm):
    echart = ECharts(ECHART, width=500, height=500)
    model = echart.get_root(document, comm)
    assert model.geo_data == {}


def test_echart_geo_data_multiple_maps(document, comm):
    geo = {"map_a": MINIMAL_GEOJSON, "map_b": MINIMAL_GEOJSON}
    echart = ECharts(ECHART, geo_data=geo, width=500, height=500)
    model = echart.get_root(document, comm)
    assert model.geo_data == geo


def test_echart_geo_data_list_geo_config(document, comm):
    echart_config = {
        "geo": [
            {"map": "map_a"},
            {"map": "map_b"},
        ],
        "series": [],
    }
    geo = {"map_a": MINIMAL_GEOJSON, "map_b": MINIMAL_GEOJSON}
    echart = ECharts(echart_config, geo_data=geo, width=500, height=500)
    model = echart.get_root(document, comm)
    assert model.geo_data == geo


def test_echart_geo_data_url_string_passes_through(document, comm):
    """URL strings are forwarded to the bokeh model as-is; the frontend fetches them."""
    echart_config = {
        "geo": {"map": "test"},
        "series": [],
    }
    url = "https://example.com/test.json"
    echart = ECharts(echart_config, geo_data={"test": url}, width=500, height=500)
    model = echart.get_root(document, comm)
    assert model.geo_data == {"test": url}


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
