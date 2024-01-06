import time

import pytest

import panel as pn

from panel.tests.util import serve_component, wait_until
from panel.util import parse_query
from panel.widgets import FloatSlider, RangeSlider, TextInput

pytestmark = pytest.mark.ui


def verify_document_location(expected_location, page):
    for param in expected_location:
        wait_until(lambda: param in page.evaluate('() => document.location'), page)  # noqa: B023
        wait_until(lambda: page.evaluate('() => document.location')[param] == expected_location[param], page)  # noqa: B023


def test_set_url_params_update_document(page):
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

    _, port = serve_component(page, app)

    expected_location = {
        'protocol': 'http:',
        'hostname': 'localhost',
        'port': f'{port}',
        'pathname': '/',
        'hash': '',
        'reload': None
    }
    verify_document_location(expected_location, page)
    wait_until(lambda: parse_query(page.evaluate('() => document.location')['search']) == {
        'range_value': [1, 2],
        'slider_value': 2,
        'text_value': 'Simple Text'
    }, page)


def test_set_hash_update_document(page):
    def app():
        """simple app to set hash at onload"""
        widget = TextInput(name='Text')

        def cb():
            pn.state.location.hash = '#123'

        pn.state.onload(cb)
        return widget

    _, port = serve_component(page, app)

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
    verify_document_location(expected_location, page)


def test_set_document_location_update_state(page):
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

    serve_component(page, app, suffix="/?text_value=Text+Value")

    # confirm value of the text input widget
    wait_until(lambda: widget.value == 'Text Value', page)
