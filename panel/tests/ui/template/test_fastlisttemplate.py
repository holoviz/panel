import pytest

try:
    from playwright.sync_api import expect
    pytestmark = [pytest.mark.ui, pytest.mark.internet]
except ImportError:
    pytestmark = [pytest.mark.skip('playwright not available')]

from panel.pane import Markdown
from panel.template import FastGridTemplate, FastListTemplate
from panel.tests.util import serve_component, wait_until


def test_fast_list_template_no_console_errors(page):
    tmpl = FastListTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    msgs, _ = serve_component(page, tmpl)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')

    known_messages = [
        "setting log level to: 'info'",
        "Websocket connection 0 is now open",
        "document idle at",
        "items were rendered successfully",
        "Automatic fallback to software WebGL has been deprecated",
    ]
    assert len([
        msg for msg in msgs if not any(known in msg.text for known in known_messages)
    ]) == 0


def test_fast_list_template_updates(page):
    tmpl = FastListTemplate()
    md = Markdown('Initial')

    tmpl.main.append(md)

    serve_component(page, tmpl)

    expect(page.locator(".markdown").locator("div")).to_have_text('Initial\n')
    md.object = 'Updated'
    expect(page.locator(".markdown").locator("div")).to_have_text('Updated\n')


CANVAS_INK = """
() => {
    const canvases = [];
    const collect = (root) => {
        root.querySelectorAll('*').forEach(el => {
            if (el.tagName === 'CANVAS' && el.classList.contains('bk-layer')) canvases.push(el);
            if (el.shadowRoot) collect(el.shadowRoot);
        });
    };
    collect(document.getElementById('pn-Modal'));
    if (!canvases.length) return null;
    return canvases.map(c => {
        if (c.width <= 300 || !c.height) return 0;
        const data = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
        let ink = 0;
        for (let i = 3; i < data.length; i += 4) { if (data[i]) ink++; }
        return ink;
    });
}
"""


@pytest.mark.parametrize('template', [FastListTemplate, FastGridTemplate])
def test_fast_template_modal_paints_bokeh_plot(page, template):
    from bokeh.plotting import figure

    from panel.pane import Bokeh

    fig = figure(width=500, height=200)
    fig.line([1, 2, 3], [3, 1, 2], line_width=4)

    tmpl = template(modal=[Bokeh(fig)])

    serve_component(page, tmpl)

    def modal_painted():
        inks = page.evaluate(CANVAS_INK)
        return bool(inks) and any(ink > 0 for ink in inks)

    tmpl.open_modal()
    wait_until(modal_painted, page)
    expect(page.locator('.pn-modal-content')).to_be_visible()

    tmpl.close_modal()
    expect(page.locator('.pn-modal-content')).to_be_hidden()

    tmpl.open_modal()
    expect(page.locator('.pn-modal-content')).to_be_visible()
    wait_until(modal_painted, page)


@pytest.mark.parametrize('sizing_mode', ['scale_both', 'stretch_both'])
def test_fast_list_template_both_sizing_modes_fill_height(page, sizing_mode):
    from bokeh.plotting import figure

    from panel.layout import Column
    from panel.pane import Bokeh

    fig = figure(sizing_mode=sizing_mode, aspect_ratio=1.5 if sizing_mode == 'scale_both' else None)
    fig.line([0, 1], [0, 1])
    tmpl = FastListTemplate()
    tmpl.main.append(Column(Bokeh(fig), min_height=100))

    serve_component(page, tmpl)

    card = page.locator(f"#main .card-margin.{sizing_mode}")
    expect(card).to_have_count(1)
    wait_until(lambda: card.bounding_box()['height'] > 300, page)
