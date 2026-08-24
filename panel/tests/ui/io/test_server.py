import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import config, state
from panel.layout import Column
from panel.template import BootstrapTemplate
from panel.tests.util import serve_component
from panel.widgets import Button, IntSlider

pytestmark = pytest.mark.ui


@pytest.mark.parametrize('prefix', ['', '/prefix/'])
def test_server_index_redirect(page, prefix):
    serve_component(page, '### App', prefix=prefix, suffix=prefix)

    expect(page.locator("h3")).to_have_text('App')

@pytest.mark.parametrize('prefix', ['', '/prefix/'])
def test_server_index_redirect_via_proxy(page, prefix, reverse_proxy):
    port, proxy = reverse_proxy
    serve_component(page, '### App', prefix=prefix, suffix=f"/proxy{prefix or '/'}", port=port, proxy=proxy)

    expect(page.locator("h3")).to_have_text('App')

@pytest.mark.parametrize('prefix', ['', '/prefix/'])
def test_server_index_page_links(page, prefix):
    serve_component(page, {'app1': '### App1', 'app2': '### App2'}, prefix=prefix, suffix=prefix, wait=False)

    card = page.locator('.card-link').nth(0)
    expect(card).to_be_attached()
    card.click()

    expect(page.locator("h3")).to_have_text('App1')

@pytest.mark.parametrize('prefix', ['', '/prefix/'])
def test_server_index_page_links_via_proxy(page, prefix, reverse_proxy):
    port, proxy = reverse_proxy
    serve_component(page, {'app1': '### App1', 'app2': '### App2'}, prefix=prefix, suffix=f"/proxy{prefix or '/'}", port=port, proxy=proxy, wait=False)

    card = page.locator('.card-link').nth(0)
    expect(card).to_be_attached()
    card.click()

    expect(page.locator("h3")).to_have_text('App1')


def test_server_reuse_sessions(page, reuse_sessions):
    def app(counts=[0]):
        content = f'### Count {counts[0]}'
        counts[0] += 1
        return content

    _, port = serve_component(page, app)

    expect(page.locator(".markdown h3")).to_have_text('Count 0')

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".markdown h3")).to_have_text('Count 1')


def test_server_reuse_sessions_with_session_key_func(page, reuse_sessions):
    config.session_key_func = lambda r: (r.path, r.arguments.get('arg', [''])[0])
    def app(counts=[0]):
        title = state.session_args.get('arg', [b''])[0].decode('utf-8')
        content = f"### Count {counts[0]}"
        tmpl = BootstrapTemplate(title=title)
        tmpl.main.append(content)
        counts[0] += 1
        return tmpl

    _, port = serve_component(page, app, suffix='/?arg=foo')

    expect(page).to_have_title('foo')
    expect(page.locator(".markdown h3")).to_have_text('Count 0')

    page.goto(f"http://localhost:{port}/?arg=bar")

    expect(page).to_have_title('bar')
    expect(page.locator(".markdown h3")).to_have_text('Count 1')


@pytest.mark.filterwarnings("ignore:remove second argument of ws_handler:DeprecationWarning")
def test_fastapi_server(page, server_implementation):
    slider = IntSlider(label="Slider", start=0, end=10, value=3)
    serve_component(page, slider)
    expect(page.locator(".noUi-target")).to_be_visible()


def test_server_dynamic_layout_with_bokeh_model_mutation(page):
    """
    Regression test for models being referenced before they are defined.

    Bokeh dispatches the events it collects at the end of a locked
    callback, so appending a new component to a layout and then mutating
    one of its Bokeh models in the same callback must not reorder the
    two patches, otherwise the client is asked to apply a change to a
    model it has never been sent.
    """
    from bokeh.models import ColumnDataSource
    from bokeh.plotting import figure

    def app():
        col = Column()
        button = Button(label='Add')

        def add(event, counter=[0]):
            counter[0] += 1
            source = ColumnDataSource(data={'x': [0, 1], 'y': [0, 1]})
            fig = figure(width=200, height=200, title=f'fig {counter[0]}')
            fig.line('x', 'y', source=source)
            col.append(Column(f'### Item {counter[0]}', fig))
            fig.title.text = f'fig {counter[0]} updated'
            source.data = {'x': [0, 1, 2], 'y': [2, 1, 0]}

        button.on_click(add)
        return Column(button, col)

    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))

    serve_component(page, app)

    for i in range(1, 6):
        page.click('button:has-text("Add")')
        expect(page.locator('.markdown h3')).to_have_count(i)
        expect(page.locator('.bk-Canvas')).to_have_count(i)

    assert not errors
