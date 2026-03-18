import json
import logging

from io import BytesIO
from unittest.mock import patch

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


def _mock_urlopen(geojson_data):
    """Return a context-manager mock for urllib.request.urlopen."""
    encoded = json.dumps(geojson_data).encode()

    class FakeResponse(BytesIO):
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

    def _urlopen(url, timeout=None):
        return FakeResponse(encoded)

    return _urlopen


def test_echart_geo_data_auto_fetch_from_cdn(document, comm, caplog):
    ECharts._geo_cache.clear()
    echart_config = {
        "geo": {"map": "world"},
        "series": [],
    }
    with patch("panel.pane.echarts.urllib.request.urlopen",
               side_effect=_mock_urlopen(MINIMAL_GEOJSON)):
        with caplog.at_level(logging.INFO):
            echart = ECharts(echart_config, width=500, height=500)
            model = echart.get_root(document, comm)
    assert model.geo_data == {"world": MINIMAL_GEOJSON}
    assert "auto-fetched" in caplog.text
    ECharts._geo_cache.clear()


def test_echart_geo_data_auto_fetch_failure_warning(document, comm, caplog):
    ECharts._geo_cache.clear()
    echart_config = {
        "geo": {"map": "nonexistent_map"},
        "series": [],
    }
    with patch("panel.pane.echarts.urllib.request.urlopen",
               side_effect=Exception("Network error")):
        with caplog.at_level(logging.WARNING):
            echart = ECharts(echart_config, width=500, height=500)
            echart.get_root(document, comm)
    assert "'nonexistent_map'" in caplog.text
    assert "geo_data" in caplog.text
    ECharts._geo_cache.clear()


def test_echart_geo_data_url_string(document, comm):
    ECharts._geo_cache.clear()
    echart_config = {
        "geo": {"map": "test"},
        "series": [],
    }
    url = "https://example.com/test.json"
    with patch("panel.pane.echarts.urllib.request.urlopen",
               side_effect=_mock_urlopen(MINIMAL_GEOJSON)):
        echart = ECharts(echart_config, geo_data={"test": url},
                         width=500, height=500)
        model = echart.get_root(document, comm)
    assert model.geo_data == {"test": MINIMAL_GEOJSON}
    ECharts._geo_cache.clear()


def test_echart_geo_data_no_warning_when_provided(document, comm, caplog):
    echart_config = {
        "geo": {"map": "test"},
        "series": [],
    }
    with caplog.at_level(logging.WARNING):
        echart = ECharts(echart_config, geo_data={"test": MINIMAL_GEOJSON},
                         width=500, height=500)
        echart.get_root(document, comm)
    assert "failed" not in caplog.text


def test_echart_geo_data_series_map_auto_fetch(document, comm):
    ECharts._geo_cache.clear()
    echart_config = {
        "series": [{"type": "map", "map": "china"}],
    }
    with patch("panel.pane.echarts.urllib.request.urlopen",
               side_effect=_mock_urlopen(MINIMAL_GEOJSON)):
        echart = ECharts(echart_config, width=500, height=500)
        model = echart.get_root(document, comm)
    assert model.geo_data == {"china": MINIMAL_GEOJSON}
    ECharts._geo_cache.clear()


def test_echart_geo_data_list_geo_config(document, comm):
    ECharts._geo_cache.clear()
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
    ECharts._geo_cache.clear()


def test_echart_geo_data_list_geo_auto_fetch(document, comm):
    ECharts._geo_cache.clear()
    echart_config = {
        "geo": [
            {"map": "map_x"},
            {"map": "map_y"},
        ],
        "series": [],
    }
    with patch("panel.pane.echarts.urllib.request.urlopen",
               side_effect=_mock_urlopen(MINIMAL_GEOJSON)):
        echart = ECharts(echart_config, width=500, height=500)
        model = echart.get_root(document, comm)
    assert "map_x" in model.geo_data
    assert "map_y" in model.geo_data
    ECharts._geo_cache.clear()


def test_echart_geo_data_url_fetch_failure_warning(document, comm, caplog):
    ECharts._geo_cache.clear()
    echart_config = {
        "geo": {"map": "test"},
        "series": [],
    }
    with patch("panel.pane.echarts.urllib.request.urlopen",
               side_effect=Exception("404 Not Found")):
        with caplog.at_level(logging.WARNING):
            echart = ECharts(echart_config,
                             geo_data={"test": "https://bad.url/test.json"},
                             width=500, height=500)
            echart.get_root(document, comm)
    assert "failed to fetch" in caplog.text
    ECharts._geo_cache.clear()


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
