import time

import param
import pytest

pytestmark = pytest.mark.ui

from panel.io.server import serve
from panel.reactive import ReactiveHTML


class ReactiveComponent(ReactiveHTML):

    count = param.Integer(default=0)

    _template = "<div id='reactive' class='reactive'></div>"

    _scripts = {'render': 'data.count += 1; reactive.innerText = `${data.count}`;'}


def test_reactive_html_set_loading_no_rerender(page, port):
    component = ReactiveComponent()

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert page.text_content(".reactive") == '1'
    component.loading = True
    time.sleep(0.1)
    assert page.text_content(".reactive") == '1'
    component.loading = False
    time.sleep(0.1)
    assert page.text_content(".reactive") == '1'

def test_reactive_html_changing_css_classes_rerenders(page, port):
    component = ReactiveComponent()

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert page.text_content(".reactive") == '1'
    component.css_classes = ['custom']
    time.sleep(0.1)
    assert page.text_content(".reactive") == '2'
    component.loading = True
    time.sleep(0.1)
    assert page.text_content(".reactive") == '2'
    component.css_classes = []
    time.sleep(0.1)
    assert page.text_content(".reactive") == '3'

def test_reactive_html_set_background_no_rerender(page, port):
    component = ReactiveComponent()

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert page.text_content(".reactive") == '1'
    component.background = 'red'
    time.sleep(0.1)
    assert page.text_content(".reactive") == '1'
    component.background = 'green'
    time.sleep(0.1)
    assert page.text_content(".reactive") == '1'
