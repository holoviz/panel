import pytest

import panel as pn

from panel.tests.util import serve_panel_widget
from panel.widgets import FloatSlider, RangeSlider, TextInput

pytestmark = pytest.mark.ui


def test_set_url_params_update_documment(page, port):
    def app():
        w1 = FloatSlider(name='Slider', start=0, end=10, css_classes=['float-slider'])
        w2 = TextInput(name='Text', css_classes=['text-input'])
        w3 = RangeSlider(name='RangeSlider', start=0, end=10, css_classes=['range-slider'])
        widgets = pn.Row(w1, w2, w3)

        if pn.state.location:
            pn.state.location.sync(w1, {'value': 'slider_value'})
            pn.state.location.sync(w2, {'value': 'text_value'})
            pn.state.location.sync(w3, {'value': 'range_value'})

        def cb():
            w1.value = 2
            w2.value = 'Simple Text'
            w3.value = (1, 2)

        pn.state.onload(cb)
        return widgets

    serve_panel_widget(page, port, app)
    page.wait_for_timeout(200)

    expected_document_location = {
        'href': f'http://localhost:{port}/?slider_value=2&range_value=%5B1%2C+2%5D&text_value=Simple+Text',
        'protocol': 'http:',
        'hostname': 'localhost',
        'port': f'{port}',
        'pathname': '/',
        'search': '?slider_value=2&range_value=%5B1%2C+2%5D&text_value=Simple+Text',
        'hash': '',
        'reload': None
    }
    document_location = page.evaluate('() => document.location')
    for param in expected_document_location:
        assert param in document_location
        assert document_location[param] == expected_document_location[param]


def test_set_hash_update_documment(page, port):
    def app():
        widget = TextInput(name='Text', css_classes=['text-input'])
        if pn.state.location:
            pn.state.location.sync(widget, {'value': 'text_value'})

        def cb():
            pn.state.location.hash = '#123'

        pn.state.onload(cb)
        return widget

    serve_panel_widget(page, port, app)
    page.wait_for_timeout(200)

    expected_document_location = {
        'href': f'http://localhost:{port}/#123',
        'protocol': 'http:',
        'hostname': 'localhost',
        'port': f'{port}',
        'pathname': '/',
        'search': '',
        'hash': '#123',
        'reload': None
    }
    document_location = page.evaluate('() => document.location')
    for param in expected_document_location:
        assert param in document_location
        assert document_location[param] == expected_document_location[param]
