import param
import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.reactive import ReactiveHTML
from panel.tests.util import serve_component, wait_until

pytestmark = pytest.mark.ui


class ReactiveComponent(ReactiveHTML):

    count = param.Integer(default=0)

    event = param.Event()

    _template = """
    <div id="reactive" class="reactive" onclick="${script('click')}"></div>
    """

    _scripts = {
        'render': 'data.count += 1; reactive.innerText = `${data.count}`;',
        'click': 'data.count += 1; reactive.innerText = `${data.count}`;',
        'event': 'data.count += 1; reactive.innerText = `${data.count}`;',
    }

class ReactiveLiteral(ReactiveHTML):

    value = param.String()

    _template = """
    <div class="reactive">{{value}}</div>
    """


def test_reactive_html_click_js_event(page):
    component = ReactiveComponent()

    serve_component(page, component)

    expect(page.locator(".reactive")).to_have_text('1')

    page.locator(".reactive").click()

    expect(page.locator(".reactive")).to_have_text('2')

    wait_until(lambda: component.count == 2, page)

def test_reactive_html_param_event(page):
    component = ReactiveComponent()

    serve_component(page, component)

    expect(page.locator(".reactive")).to_have_text('1')

    component.param.trigger('event')

    expect(page.locator(".reactive")).to_have_text('2')

    component.param.trigger('event')

    expect(page.locator(".reactive")).to_have_text('3')

    component.param.trigger('event')
    component.param.trigger('event')

    expect(page.locator(".reactive")).to_have_text('5')

    wait_until(lambda: component.count == 5, page)

def test_reactive_html_set_loading_no_rerender(page):
    component = ReactiveComponent()

    serve_component(page, component)

    expect(page.locator(".reactive")).to_have_text('1')

    component.loading = True
    expect(page.locator(".reactive")).to_have_text('1')

    component.loading = False
    expect(page.locator(".reactive")).to_have_text('1')

def test_reactive_html_changing_css_classes_rerenders(page):
    component = ReactiveComponent()

    serve_component(page, component)

    expect(page.locator(".reactive")).to_have_text('1')

    component.css_classes = ['custom']

    expect(page.locator(".reactive")).to_have_text('1')

    component.loading = True

    expect(page.locator(".reactive")).to_have_text('1')

    component.css_classes = []

    expect(page.locator(".reactive")).to_have_text('1')

def test_reactive_html_set_background_no_rerender(page):
    component = ReactiveComponent()

    serve_component(page, component)

    expect(page.locator(".reactive")).to_have_text('1')

    component.styles = dict(background='red')

    expect(page.locator(".reactive")).to_have_text('1')

    component.styles = dict(background='green')

    expect(page.locator(".reactive")).to_have_text('1')

def test_reactive_literal_backtick(page):
    component = ReactiveLiteral(value="Backtick: `")

    serve_component(page, component)

    expect(page.locator(".reactive")).to_have_text('Backtick: `')
