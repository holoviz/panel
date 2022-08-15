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

    href = page.evaluate('() => document.location.href')
    expected_params = '?slider_value=2&range_value=%5B1%2C+2%5D&text_value=Simple+Text'
    document_params = href[href.find('?'):]
    assert document_params == expected_params
