import logging
import re

import pandas as pd
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

# Emulates a host like Jupyter, which owns the document element.
STRIP_THEME_MANAGED = """
new MutationObserver((_, observer) => {
  if (document.documentElement) {
    document.documentElement.removeAttribute("data-theme-managed")
    observer.disconnect()
  }
}).observe(document, {childList: true})
"""

TABULATOR_HEADER_STYLE = """el => {
  const style = getComputedStyle(el)
  return [style.backgroundColor, style.color, style.borderBottomColor]
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


def test_widgetbox_disables_widgets(page, panel_ui):
    box = panel_ui.WidgetBox(panel_ui.TextInput(label='Name'), disabled=True)
    serve_component(page, box)

    expect(page.locator('input')).to_be_disabled()

    box.disabled = False

    expect(page.locator('input')).to_be_enabled()


COUNT_DEFERRED_TASKS = """
window.deferred_tasks = 0
const post = MessagePort.prototype.postMessage
MessagePort.prototype.postMessage = function(...args) {
  window.deferred_tasks++
  return post.apply(this, args)
}
"""


def test_tabulator_in_inactive_tab_does_not_spin(page, panel_ui):
    df = pd.DataFrame({'a': range(5)})
    tabs = panel_ui.Tabs(('A', 'first'), ('B', panel_ui.Tabulator(df)))

    page.add_init_script(COUNT_DEFERRED_TASKS)
    serve_component(page, tabs)
    expect(page.get_by_role('tab', name='A')).to_be_visible()
    page.wait_for_timeout(500)

    page.evaluate("() => { window.deferred_tasks = 0 }")
    page.wait_for_timeout(500)
    assert page.evaluate("() => window.deferred_tasks") < 100

    page.get_by_role('tab', name='B').click()
    expect(page.locator('.tabulator-row')).to_have_count(len(df))


def test_tabulator_in_unmanaged_host_matches_served_app(page, panel_ui):
    from panel_material_ui.layout import MaterialWrapper

    design = panel_ui.MaterialUIDesign
    df = pd.DataFrame({'a': [1, 2]})

    serve_component(page, panel_ui.Column(panel_ui.Tabulator(df, design=design), design=design))
    served = page.locator('.tabulator-header').evaluate(TABULATOR_HEADER_STYLE)

    page.add_init_script(STRIP_THEME_MANAGED)
    serve_component(page, MaterialWrapper(panel_ui.Tabulator(df, design=design), design=design))
    assert not page.evaluate("() => document.documentElement.hasAttribute('data-theme-managed')")
    unmanaged = page.locator('.tabulator-header').evaluate(TABULATOR_HEADER_STYLE)

    assert unmanaged == served
    assert served[0] != 'rgba(0, 0, 0, 0)'
