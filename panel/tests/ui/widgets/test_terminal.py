from itertools import count

import pytest

pytest.importorskip("playwright")

from playwright.sync_api import expect

from panel.layout import Column, Tabs
from panel.pane import Markdown
from panel.tests.util import serve_component, wait_until
from panel.widgets import Button, Terminal

pytestmark = pytest.mark.ui

TERMINAL_TEXT = r"""async () => {
  const model = [...Bokeh.documents[0].all_models].find(m => m.type.endsWith('Terminal'))
  const term = Bokeh.index.find_one_by_id(model.id).term
  await new Promise(resolve => term.write('', resolve))
  const buffer = term.buffer.active
  return [...Array(buffer.length).keys()].map(i => buffer.getLine(i).translateToString(true)).join('\n')
}"""


def _assert_terminal_text(page, expected):
    def check():
        assert page.evaluate(TERMINAL_TEXT).rstrip('\n') == expected.rstrip('\n')

    wait_until(check, page)


def _serve_terminal(page, dynamic=True):
    terminal = Terminal(height=300, sizing_mode='stretch_width')
    counter = count()
    write = Button(label='Write a line')
    write.on_click(lambda event: terminal.write(f'line {next(counter)}\n'))
    repeat = Button(label='Write repeated line')
    repeat.on_click(lambda event: terminal.write('repeat\n'))
    clear = Button(label='Clear')
    clear.on_click(terminal.clear)
    tabs = Tabs(('Other', Markdown('other tab')), ('Log', terminal), dynamic=dynamic, active=1)
    msgs, _ = serve_component(page, Column(write, repeat, clear, tabs))
    expect(page.locator('.xterm')).to_be_visible()
    return terminal, tabs, msgs


def _switch_tab(page, tabs, active):
    page.locator('.bk-tab').nth(active).click()
    wait_until(lambda: tabs.active == active, page)
    if active == 1:
        expect(page.locator('.xterm')).to_be_visible()
    else:
        expect(page.locator('.xterm')).to_be_hidden()


@pytest.mark.parametrize('dynamic', [False, True])
def test_terminal_preserves_history_in_tabs(page, dynamic):
    terminal, tabs, msgs = _serve_terminal(page, dynamic)
    write = page.get_by_role('button', name='Write a line', exact=True)
    expected = ''

    for i in range(3):
        write.click()
        expected += f'line {i}\n'
        _assert_terminal_text(page, expected)

    for _ in range(3):
        _switch_tab(page, tabs, 0)
        _switch_tab(page, tabs, 1)
        _assert_terminal_text(page, expected)

    write.click()
    expected += 'line 3\n'
    _assert_terminal_text(page, expected)

    _switch_tab(page, tabs, 0)
    for i in range(4, 6):
        write.click()
        expected += f'line {i}\n'
        wait_until(lambda expected=expected: terminal.output == expected, page)
    _switch_tab(page, tabs, 1)
    _assert_terminal_text(page, expected)

    for _ in range(2):
        page.get_by_role('button', name='Write repeated line', exact=True).click()
        expected += 'repeat\n'
        _assert_terminal_text(page, expected)
    _switch_tab(page, tabs, 0)
    _switch_tab(page, tabs, 1)
    _assert_terminal_text(page, expected)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


@pytest.mark.parametrize('clear_while_hidden', [False, True])
def test_terminal_clear_does_not_restore_history(page, clear_while_hidden):
    terminal, tabs, msgs = _serve_terminal(page)
    write = page.get_by_role('button', name='Write a line', exact=True)

    for i in range(3):
        write.click()
        _assert_terminal_text(page, ''.join(f'line {j}\n' for j in range(i + 1)))

    if clear_while_hidden:
        _switch_tab(page, tabs, 0)
    page.get_by_role('button', name='Clear', exact=True).click()
    wait_until(lambda: terminal.output == '', page)
    if not clear_while_hidden:
        _assert_terminal_text(page, '')
        _switch_tab(page, tabs, 0)
    _switch_tab(page, tabs, 1)
    _assert_terminal_text(page, '')

    write.click()
    _assert_terminal_text(page, 'line 3\n')
    _switch_tab(page, tabs, 0)
    _switch_tab(page, tabs, 1)
    _assert_terminal_text(page, 'line 3\n')

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []
