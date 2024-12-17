import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel import config, state
from panel.template import BootstrapTemplate
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui


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
