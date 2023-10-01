import pytest

pytestmark = pytest.mark.ui

from panel.config import config
from panel.io.state import state
from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until


def test_browser_sync(page):
    info = {}
    def app():
        with config.set(browser_info=True):
            sync = lambda *events: info.update({e.name: e.new for e in events})
            state.browser_info.param.watch(sync, list(state.browser_info.param))
            Markdown('# Test').servable()

    serve_component(page, app)

    wait_until(lambda: bool(info), page)

    assert info['dark_mode'] == page.evaluate("() => window.matchMedia('(prefers-color-scheme: dark)').matches")
    assert info['device_pixel_ratio'] == page.evaluate('() => window.devicePixelRatio')
    assert info['language'] == page.evaluate('() => navigator.language')
    assert info['webdriver'] == page.evaluate('() => navigator.webdriver')
    assert info['timezone'] == page.evaluate('() => Intl.DateTimeFormat().resolvedOptions().timeZone')
    assert info['timezone_offset'] == page.evaluate('() => new Date().getTimezoneOffset()')
