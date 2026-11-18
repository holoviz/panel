import os
import time

import pytest

try:
    from playwright.sync_api import expect

    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip("playwright not available")

import panel as pn

from panel.tests.util import (
    _STYLESHEETS_SETTLED, linux_only, proxied_oauth_provider, run_panel_serve,
    serve_component, wait_for_port, wait_until, write_file,
)
from panel.util import parse_query
from panel.widgets import FloatSlider, RangeSlider, TextInput


def verify_document_location(expected_location, page):
    for param in expected_location:
        wait_until(lambda: param in page.evaluate('() => document.location'), page)  # noqa: B023
        wait_until(lambda: page.evaluate('() => document.location')[param] == expected_location[param], page)  # noqa: B023


def test_set_url_params_update_document(page):
    def app():
        """Simple app to set url by widgets' values"""
        w1 = FloatSlider(label='Slider', start=0, end=10)
        w2 = TextInput(label='Text')
        w3 = RangeSlider(label='RangeSlider', start=0, end=10)
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
        'hostname': '127.0.0.1',
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
        widget = TextInput(label='Text')

        def cb():
            pn.state.location.hash = '#123'

        pn.state.onload(cb)
        return widget

    _, port = serve_component(page, app)

    expected_location = {
        'href': f'http://127.0.0.1:{port}/#123',
        'protocol': 'http:',
        'hostname': '127.0.0.1',
        'port': f'{port}',
        'pathname': '/',
        'search': '',
        'hash': '#123',
        'reload': None
    }
    verify_document_location(expected_location, page)


def test_set_document_location_update_state(page):
    widget = TextInput(label='Text')

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


def test_set_nested_pathname_then_load_markdown_no_console_errors(page):
    markdown_text = "Dynamically loaded markdown"

    def app():
        layout = pn.Column(pn.pane.Markdown("Initial markdown"))

        def cb():
            pn.state.location.pathname = "/foo/bar"
            layout.append(pn.pane.Markdown(markdown_text))

        pn.state.onload(cb)
        return layout

    msgs, _ = serve_component(page, app)

    expect(page.locator(".markdown")).to_have_count(2)

    assert [
        msg for msg in msgs
        if msg.type == 'error' and 'favicon' not in msg.location['url']
    ] == []


_NAVIGATING_APP = """
import panel as pn

button = pn.widgets.Button(name="Navigate")
at = pn.widgets.StaticText(value=pn.bind(lambda p: f"At {{p}}", pn.state.location.param.pathname))
layout = pn.Column(button, at, pn.pane.Markdown("Initial markdown"))

def navigate(*_):
    pn.state.location.pathname = {pathname!r}
    layout.append(pn.pane.Markdown("Dynamically loaded markdown"))

if {on_click!r}:
    button.on_click(navigate)
else:
    pn.state.onload(navigate)
layout.servable()
"""


@linux_only
@pytest.mark.parametrize('pathname,proxy_mode,on_click', [
    ('/foo/bar', None, False),
    ('/foo/bar/', None, False),
    ('/foo/', None, False),
    ('/foo/bar', None, True),
    # Once the browser reported the url it loaded the proxy prefix is known
    ('/foo/bar/', 'stripped', True),
    # Before that only a configured root path declares it
    ('/foo/bar/', 'root_path', False),
], ids=['onload', 'trailing_slash', 'shallow', 'click', 'proxy', 'proxy_root_path'])
def test_set_nested_pathname_with_panel_serve_resolves_resources_from_root(
    py_file, port, page, pathname, proxy_mode, on_click
):
    app_name = os.path.basename(py_file.name)[:-3]
    requests = []
    page.on('response', lambda r: requests.append((r.status, r.url)))
    page.on('requestfailed', lambda r: requests.append(('failed', r.url)))

    with proxied_oauth_provider() as proxy:
        # The proxy strips its prefix, so the server only sees it if it is
        # configured as the root path.
        prefix = '/proxy' if proxy_mode else ''
        write_file(_NAVIGATING_APP.format(pathname=f'{prefix}{pathname}', on_click=on_click), py_file.file)
        args = ["--port", str(port), py_file.name]
        if proxy_mode:
            args += ["--allow-websocket-origin", f"localhost:{proxy['port']}"]
        if proxy_mode == 'root_path':
            args += ["--root-path", "/proxy/"]
        with run_panel_serve(args) as p:
            port = wait_for_port(p.stdout)
            if proxy_mode:
                proxy['upstream'] = port
                url = f"http://localhost:{proxy['port']}/proxy/{app_name}"
            else:
                url = f"http://localhost:{port}/{app_name}"
            msgs = []
            page.on("console", lambda msg: msgs.append(msg.text))
            page.goto(url)
            if on_click:
                wait_until(lambda: any("Websocket connection 0 is now open" in msg for msg in msgs), page)
                page.wait_for_function(_STYLESHEETS_SETTLED, timeout=15000)
                # The server has to know the url the browser loaded
                expect(page.get_by_text(f"At {prefix}/{app_name}")).to_be_visible()
                page.locator(".bk-btn").click()

            expect(page.locator(".markdown")).to_have_count(2)
            wait_until(lambda: page.url.endswith(f'{prefix}{pathname}'), page)
            page.wait_for_function(_STYLESHEETS_SETTLED, timeout=15000)

    assert [(status, url) for status, url in requests if status == 'failed' or status >= 400] == []
    assert [url for _, url in requests if '/foo/' in url] == []
    if proxy_mode:
        assert [url for _, url in requests if url.startswith('http') and '/proxy/' not in url] == []


def test_reload_set_at_build_time_navigates_on_pathname_change(page):
    def app():
        pn.state.location.reload = True
        button = pn.widgets.Button(label='Navigate')
        button.on_click(lambda e: setattr(pn.state.location, 'pathname', '/other'))
        return button

    serve_component(page, app)

    page.evaluate("() => { window.__marker = true }")
    page.locator('.bk-btn').click()

    # Evaluating while the page navigates raises, so wait for the load to finish
    page.wait_for_url('**/other')
    assert page.evaluate("() => window.__marker === undefined")


def test_default_location_pathname_change_does_not_reload(page):
    def app():
        button = pn.widgets.Button(label='Navigate')
        button.on_click(lambda e: setattr(pn.state.location, 'pathname', '/other'))
        return button

    serve_component(page, app)

    page.evaluate("() => { window.__marker = true }")
    page.locator('.bk-btn').click()

    wait_until(lambda: page.evaluate("() => document.location.pathname") == '/other', page)
    assert page.evaluate("() => window.__marker") is True


def test_disabling_reload_does_not_reload_page(page):
    def app():
        pn.state.location.reload = True
        button = pn.widgets.Button(label='Disable')
        button.on_click(lambda e: setattr(pn.state.location, 'reload', False))
        return button

    serve_component(page, app)

    page.evaluate("() => { window.__marker = true }")
    page.locator('.bk-btn').click()

    time.sleep(1)
    assert page.evaluate("() => window.__marker") is True
