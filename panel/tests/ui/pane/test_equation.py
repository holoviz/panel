import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.pane import LaTeX
from panel.tests.util import serve_component

pytestmark = pytest.mark.ui

def test_latex_mathjax_renderer(page):
    ltx = LaTeX('$1+1$', renderer='mathjax')

    serve_component(page, ltx)

    expect(page.locator('mjx-container')).to_have_count(1)

def test_latex_katex_renderer(page):
    ltx = LaTeX('$1+1$', renderer='katex')

    serve_component(page, ltx)

    expect(page.locator('.katex-html')).to_have_count(1)
