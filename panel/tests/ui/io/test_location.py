import time

import pytest

import panel as pn

from panel.io.server import serve
from panel.tests.util import serve_panel_widget
from panel.util import parse_query
from panel.widgets import FloatSlider, RangeSlider, TextInput

pytestmark = pytest.mark.ui


def verify_document_location(expected_location, actual_location):
    for param in expected_location:
        assert param in actual_location
        assert actual_location[param] == expected_location[param]


def test_set_url_params_update_document(page, port):
    def app():
        """Simple app to set url by widgets' values"""
        w1 = FloatSlider(name='Slider', start=0, end=10)
        w2 = TextInput(name='Text')
        w3 = RangeSlider(name='RangeSlider', start=0, end=10)
        widgets = pn.Row(w1, w2, w3)

        if pn.state.location:
            pn.state.location.sync(w1, {'value': 'slider_value'})
            time.sleep(0.1)
            pn.state.location.sync(w2, {'value': 'text_value'})
            time.sleep(0.1)
            pn.state.location.sync(w3, {'value': 'range_value'})

        def cb():
            w1.value = 2
            time.sleep(0.1)
            w2.value = 'Simple Text'
            time.sleep(0.1)
            w3.value = (1, 2)

        pn.state.onload(cb)
        return widgets

    serve_panel_widget(page, port, app)
    page.wait_for_timeout(500)

    expected_location = {
        'protocol': 'http:',
        'hostname': 'localhost',
        'port': f'{port}',
        'pathname': '/',
        'hash': '',
        'reload': None
    }
    actual_location = page.evaluate('() => document.location')
    verify_document_location(expected_location, actual_location)
    assert parse_query(actual_location['search']) == {
        'range_value': [1, 2],
        'slider_value': 2,
        'text_value': 'Simple Text'
    }


def test_set_hash_update_documment(page, port):
    def app():
        """simple app to set hash at onload"""
        widget = TextInput(name='Text')

        def cb():
            pn.state.location.hash = '#123'

        pn.state.onload(cb)
        return widget

    serve_panel_widget(page, port, app)
    page.wait_for_timeout(200)

    expected_location = {
        'href': f'http://localhost:{port}/#123',
        'protocol': 'http:',
        'hostname': 'localhost',
        'port': f'{port}',
        'pathname': '/',
        'search': '',
        'hash': '#123',
        'reload': None
    }
    actual_location = page.evaluate('() => document.location')
    verify_document_location(expected_location, actual_location)


def test_set_document_location_update_state(page, port):
    widget = TextInput(name='Text')

    def app():
        if pn.state.location:
            pn.state.location.sync(widget, {'value': 'text_value'})

        def cb():
            """Do nothing callback"""
            # validate value of search in pn.state.location
            assert pn.state.location.search == '?text_value=Text+Value'

        pn.state.onload(cb)
        return widget

    serve(app, port=port, threaded=True, show=False)
    time.sleep(0.2)
    page.goto(f"http://localhost:{port}/?text_value=Text+Value")
    page.wait_for_timeout(200)

    # confirm value of the text input widget
    assert widget.value == 'Text Value'
