import pytest

try:
    from playwright.sync_api import expect
    pytestmark = pytest.mark.ui
except ImportError:
    pytestmark = pytest.mark.skip('playwright not available')

from panel.config import config
from panel.pane import Markdown
from panel.tests.util import serve_component


def test_global_loading_indicator(page):
    def app():
        config.global_loading_spinner = True
        return Markdown('Blah')

    serve_component(page, app)

    expect(page.locator("body")).not_to_have_class('pn-loading')
