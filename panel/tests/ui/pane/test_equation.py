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

def test_latex_katex_hline_is_painted(page):
    ltx = LaTeX(r'$\begin{array}{c|c} a & b \\ \hline c & d \end{array}$', renderer='katex')

    serve_component(page, ltx)

    hline = page.locator('.katex-html .hline')
    expect(hline).to_have_count(1)
    box = hline.bounding_box()
    assert box is not None
    assert box['width'] > 0 and box['height'] > 0
    assert hline.evaluate('el => getComputedStyle(el).borderBottomStyle') == 'solid'

def test_latex_katex_visual_output_replaces_mathml(page):
    ltx = LaTeX(r'$\sqrt{x}\ \frac{1}{2}$', renderer='katex')

    serve_component(page, ltx)

    html = page.locator('.katex-html')
    expect(html).to_have_count(1)
    assert html.evaluate('el => getComputedStyle(el).display') != 'none'
    mathml = page.locator('.katex-mathml')
    assert mathml.evaluate('el => getComputedStyle(el).position') == 'absolute'
