import logging
import re

import pytest

from panel.tests.util import serve_component, wait_until

pytest.importorskip("playwright")

from playwright.sync_api import expect

pytestmark = pytest.mark.ui

# xterm renders to a canvas, so the text has to be read from its buffer.
TERMINAL_TEXT = """() => {
  const model = [...Bokeh.documents[0].all_models].find(m => m.type.endsWith('Terminal'))
  const buffer = Bokeh.index.find_one_by_id(model.id).term.buffer.active
  return [...Array(buffer.length).keys()].map(i => buffer.getLine(i).translateToString(true)).join('\\n')
}"""


def test_debugger_counts_and_clears_logs(page, panel_ui):
    debugger = panel_ui.Debugger(collapsed=False, level=logging.INFO)

    def log(event):
        logger = logging.getLogger('panel.callbacks')
        logger.info('Info message')
        logger.error('First error')
        logger.error('Second error')

    button = panel_ui.Button(label='Log', on_click=log)
    msgs, _ = serve_component(page, panel_ui.Column(button, debugger))

    page.locator('button', has_text='Log').click()

    expect(page.locator('.MuiChip-label', has_text='2 errors')).to_be_visible()
    # Panel's own session logs are counted as well.
    expect(page.locator('.MuiChip-label', has_text=re.compile(r'\d+ infos?'))).to_be_visible()
    wait_until(lambda: 'Second error' in page.evaluate(TERMINAL_TEXT), page)

    page.get_by_label('Acknowledge logs and clear').click()

    expect(page.locator('.MuiChip-label', has_text='errors')).to_be_hidden()
    wait_until(lambda: debugger._number_of_errors == 0, page)
    assert [m for m in msgs if m.type == 'error' and 'favicon' not in m.location['url']] == []


def test_modal_create_button_opens_and_closes(page, panel_ui):
    modal = panel_ui.Modal('Modal content')
    serve_component(page, panel_ui.Column(modal.create_button('show', label='Open'), modal))

    page.locator('button', has_text='Open').click()

    expect(page.locator('.MuiDialog-root')).to_contain_text('Modal content')
    wait_until(lambda: modal.open, page)

    page.locator('.MuiDialog-root button[aria-label="close"]').click()

    expect(page.locator('.MuiDialog-root')).to_have_count(0)
    wait_until(lambda: not modal.open, page)


def test_modal_background_close(page, panel_ui):
    modal = panel_ui.Modal('Modal content', open=True, background_close=False)
    serve_component(page, modal)

    expect(page.locator('.MuiDialog-root')).to_contain_text('Modal content')
    page.mouse.click(5, 5)
    page.wait_for_timeout(500)

    expect(page.locator('.MuiDialog-root')).to_contain_text('Modal content')
    assert modal.open
