import time

import param
import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.io.server import serve
from panel.reactive import ReactiveHTML


class ReactiveComponent(ReactiveHTML):

    count = param.Integer(default=0)

    _template = """
    <div id="reactive" class="reactive" onclick="${script('click')}"></div>
    """

    _scripts = {
        'render': 'data.count += 1; reactive.innerText = `${data.count}`;',
        'click': 'data.count += 1; reactive.innerText = `${data.count}`;'
    }

class ReactiveLiteral(ReactiveHTML):

    value = param.String()

    _template = """
    <div class="reactive">{{value}}</div>
    """


def test_reactive_html_click_js_event(page, port):
    component = ReactiveComponent()

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".reactive")).to_have_text('1')

    page.locator(".reactive").click()

    expect(page.locator(".reactive")).to_have_text('2')

    time.sleep(0.2)

    assert component.count == 2

def test_reactive_html_set_loading_no_rerender(page, port):
    component = ReactiveComponent()

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".reactive")).to_have_text('1')
    component.loading = True
    time.sleep(0.1)
    expect(page.locator(".reactive")).to_have_text('1')
    component.loading = False
    time.sleep(0.1)
    expect(page.locator(".reactive")).to_have_text('1')

def test_reactive_html_changing_css_classes_rerenders(page, port):
    component = ReactiveComponent()

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.5)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".reactive")).to_have_text('1')

    component.css_classes = ['custom']
    time.sleep(0.1)
    expect(page.locator(".reactive")).to_have_text('1')

    component.loading = True
    time.sleep(0.1)
    expect(page.locator(".reactive")).to_have_text('1')

    component.css_classes = []
    time.sleep(0.1)
    expect(page.locator(".reactive")).to_have_text('1')

def test_reactive_html_set_background_no_rerender(page, port):
    component = ReactiveComponent()

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".reactive")).to_have_text('1')

    component.styles = dict(background='red')
    time.sleep(0.1)
    expect(page.locator(".reactive")).to_have_text('1')

    component.styles = dict(background='green')
    time.sleep(0.1)
    expect(page.locator(".reactive")).to_have_text('1')

def test_reactive_literal_backtick(page, port):
    component = ReactiveLiteral(value="Backtick: `")

    serve(component, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".reactive")).to_have_text('Backtick: `')
