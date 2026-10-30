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


class SharedCallback(ReactiveHTML):

    _template = """
    <button id="btn1" onclick=${_click}>One</button>
    <button id="btn2" onclick=${_click}>Two</button>
    <button id="solo" onclick=${_solo}>Solo</button>
    """

    def __init__(self, **params):
        super().__init__(**params)
        self.nodes = []

    def _click(self, event):
        self.nodes.append(event.node)

    def _solo(self, event):
        self.nodes.append(event.node)


def test_reactive_html_shared_callback_reports_clicked_node(page):
    component = SharedCallback()

    serve_component(page, component)

    page.get_by_text("One").click()
    page.get_by_text("Two").click()
    page.get_by_text("Solo").click()

    wait_until(lambda: component.nodes == ['btn1', 'btn2', 'solo'], page)


class Recorder(ReactiveHTML):

    def __init__(self, **params):
        super().__init__(**params)
        self.events = []

    def _record(self, event):
        self.events.append((event.node, event.data['type']))


class MultiEvent(Recorder):

    _template = """
    <input id="i1" onclick=${_record} onchange=${_record}></input>
    <input id="i2" onclick=${_record} onchange=${_record}></input>
    """


class Nested(Recorder):

    _template = """
    <div id="outer" onclick=${_record}><span id="inner" onclick=${_record}>Inner</span><b id="pad">Pad</b></div>
    """


class Looped(Recorder):

    items = param.List(default=['a', 'b', 'c'])

    _template = """
    <div id="wrap">
    {% for item in items %}
    <button id="btn{{ loop.index0 }}" onclick=${_record}>{{ item }}</button>
    {% endfor %}
    </div>
    """


def test_reactive_html_shared_callback_reports_event_name(page):
    component = MultiEvent()

    serve_component(page, component)

    page.locator("[id^=i2-]").click()
    page.locator("[id^=i2-]").fill("x")
    page.locator("[id^=i1-]").click()
    page.locator("[id^=i1-]").fill("y")
    page.locator("[id^=i2-]").click()

    wait_until(lambda: ('i2', 'onchange') in component.events, page)
    assert ('i2', 'onclick') in component.events
    assert ('i1', 'onclick') in component.events
    assert ('i1', 'onchange') in component.events


def test_reactive_html_shared_callback_nested_nodes(page):
    component = Nested()

    serve_component(page, component)

    page.get_by_text("Inner").click()
    wait_until(lambda: len(component.events) == 2, page)
    assert sorted(n for n, _ in component.events) == ['inner', 'outer']
    component.events.clear()

    page.get_by_text("Pad").click()
    wait_until(lambda: component.events == [('outer', 'onclick')], page)


def test_reactive_html_shared_callback_in_for_loop(page):
    component = Looped()

    serve_component(page, component)

    page.get_by_text("b", exact=True).click()
    page.get_by_text("c", exact=True).click()

    wait_until(lambda: [n for n, _ in component.events] == ['btn1-1', 'btn2-2'], page)
