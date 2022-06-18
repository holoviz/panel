import sys
import time

import pytest

from playwright.sync_api import expect

pytestmark = pytest.mark.ui

try:
    from pandas._testing import makeMixedDataFrame
except ImportError:
    pytestmark = pytest.mark.skip('pandas not available')


from panel.io.server import serve
from panel.widgets import Tabulator


@pytest.fixture
def df_mixed():
    df = makeMixedDataFrame()
    df.index = [f'idx{i}' for i in range(len(df))]
    return df


def wait_until(fn, timeout=5000, interval=100):
    while timeout > 0:
        if fn():
            return True
        else:
            time.sleep(interval / 1000)
            timeout -= interval
    # To raise the False assert
    assert fn()


def get_ctrl_modifier():
    if sys.platform in ['linux', 'win32']:
        return 'Control'
    elif sys.platform == 'darwin':
        return 'Meta'
    else:
        raise ValueError(f'No control modifier defined for platform {sys.platform}')


def test_tabulator_default(page, port, df_mixed):
    nrows, ncols = df_mixed.shape
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_ncols = ncols + 2  # _index + index + data columns

    # Check that the whole table content is on the page
    table = page.locator('.bk.pnx-tabulator.tabulator')
    expect(table).to_have_text(
        'index\nA\nB\nC\nD\nidx0\n0.0\n0.0\nfoo1\n2009-01-01 00:00:00\nidx1\n1.0\n1.0\nfoo2\n2009-01-02 00:00:00\nidx2\n2.0\n0.0\nfoo3\n2009-01-05 00:00:00\nidx3\n3.0\n1.0\nfoo4\n2009-01-06 00:00:00\nidx4\n4.0\n0.0\nfoo5\n2009-01-07 00:00:00',  # noqa
        use_inner_text=True
    )

    # Check that the default layout is fitDataTable
    assert widget.layout == 'fit_data_table'
    assert table.get_attribute('tabulator-layout') == 'fitDataTable'

    # Check the table has the right number of rows
    rows = page.locator('.tabulator-row')
    assert rows.count() == nrows

    # Check that the hidden _index column is added by Panel
    cols = page.locator(".tabulator-col")
    assert cols.count() == expected_ncols
    assert cols.nth(0).get_attribute('tabulator-field') == '_index'
    assert cols.nth(0).is_hidden()

    # Check that the first visible is the index column
    assert widget.show_index
    assert page.locator('text="index"').is_visible()
    assert cols.nth(1).is_visible()

    # Check that the columns are sortable by default
    assert page.locator(".tabulator-sortable").count() == expected_ncols
    # And that none of them is sorted on start
    for i in range(expected_ncols):
        assert cols.nth(i).get_attribute('aria-sort') == 'none'


def test_tabulator_buttons_display(page, port, df_mixed):
    nrows, ncols = df_mixed.shape
    icon_text = 'icon'
    widget = Tabulator(df_mixed, buttons={'Print': icon_text})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_ncols = ncols + 3  # _index + index + data columns + button col

    # Check that an additional column has been added to the table
    # with no header title
    cols = page.locator(".tabulator-col")
    expect(cols).to_have_count(expected_ncols)
    button_col_idx = expected_ncols - 1
    assert not cols.nth(button_col_idx).get_attribute('tabulator-field')
    assert cols.nth(button_col_idx).inner_text() == '\xa0'
    assert cols.nth(button_col_idx).is_visible()

    # Check the button column has the right content
    icons = page.locator(f'text="{icon_text}"')
    assert icons.all_inner_texts() == [icon_text] * nrows

    # Check the buttons are centered
    for i in range(icons.count()):
        assert 'text-align: center' in icons.nth(i).get_attribute('style')


def test_tabulator_buttons_event(page, port, df_mixed):
    button_col_name = 'Print'
    widget = Tabulator(df_mixed, buttons={button_col_name: 'icon'})

    state = []
    expected_state = [(button_col_name, 0, None)]

    def cb(e):
        state.append((e.column, e.row, e.value))

    widget.on_click(cb)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")
    icon = page.locator("text=icon").first
    icon.wait_for()
    # Click on the first button
    icon.click()
    assert wait_until(lambda: state == expected_state)


def test_tabulator_formatters():
    pass


def test_tabulator_editors():
    pass


def test_tabulator_alignment():
    pass


def test_tabulator_styling():
    pass


def test_tabulator_theming():
    pass


def test_tabulator_selection_selectable_by_default(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    assert widget.selectable
    # Click on the first row of the index column to select the row
    rows = page.locator('.tabulator-row')
    c0 = page.locator('text="idx0"')
    c0.wait_for()
    c0.click()
    assert wait_until(lambda: widget.selection == [0])
    assert 'tabulator-selected' in rows.first.get_attribute('class')
    for i in range(1, rows.count()):
        assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')


def test_tabulator_selection_selectable_one_at_a_time(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    rows = page.locator('.tabulator-row')
    # Click on the first row of the index column to select the row
    c0 = page.locator('text="idx0"')
    c0.wait_for()
    c0.click()
    assert wait_until(lambda: widget.selection == [0])
    # Click on the second row should deselect the first one
    page.locator('text="idx1"').click()
    assert wait_until(lambda: widget.selection == [1])
    for i in range(rows.count()):
        if i == 1:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    # Clicking again on the second row should not change anything
    page.locator('text="idx1"').click()
    assert wait_until(lambda: widget.selection == [1])
    for i in range(rows.count()):
        if i == 1:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')


def test_tabulator_selection_selectable_ctrl(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    rows = page.locator('.tabulator-row')
    # Click on the first row of the index column to select the row
    c0 = page.locator('text="idx0"')
    c0.wait_for()
    c0.click()
    # Click on the thrid row with CTRL pressed should add that row to the selection
    modifier = get_ctrl_modifier()
    page.locator("text=idx2").click(modifiers=[modifier])
    expected_selection = [0, 2]
    assert wait_until(lambda: widget.selection == expected_selection)
    for i in range(rows.count()):
        if i in expected_selection:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    # Clicking again on the third row with CTRL pressed should remove the row from the selection
    page.locator("text=idx2").click(modifiers=[modifier])
    expected_selection = [0]
    assert wait_until(lambda: widget.selection == expected_selection)
    for i in range(rows.count()):
        if i in expected_selection:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')


def test_tabulator_selection_selectable_shift(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    rows = page.locator('.tabulator-row')
    # Click on the first row of the index column to select the row
    c0 = page.locator('text="idx0"')
    c0.wait_for()
    c0.click()
    # Click on the thrid row with SHIFT pressed should select the 2nd row too
    page.locator("text=idx2").click(modifiers=['Shift'])
    expected_selection = [0, 1, 2]
    assert wait_until(lambda: widget.selection == expected_selection)
    for i in range(rows.count()):
        if i in expected_selection:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')


def test_tabulator_selection_selectable_disabled(page, port, df_mixed):
    widget = Tabulator(df_mixed, selectable=False)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Click on the first row of the index column
    rows = page.locator('.tabulator-row')
    c0 = page.locator('text="idx0"')
    c0.wait_for()
    c0.click()
    # Wait for a potential selection event to be propagated, this should not
    # be the case.
    time.sleep(0.2)
    assert widget.selection == []
    for i in range(rows.count()):
        assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')


def test_tabulator_selection_default_selection(page, port, df_mixed):
    selection = [0, 2]
    widget = Tabulator(df_mixed, selection=[0, 2])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    rows = page.locator('.tabulator-row')

    # Check that the rows in the selection are selected in the front-end
    for i in range(rows.count()):
        if i in selection:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')


def test_tabulator_selection_selectable_checkbox_all(page, port, df_mixed):
    widget = Tabulator(df_mixed, selectable='checkbox')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Select the first checkbox and check it
    checkboxes = page.locator('input[type="checkbox"]')
    checkboxes.first.wait_for()
    checkboxes.first.check()
    # All the checkboxes should be checked
    for i in range(checkboxes.count()):
        assert checkboxes.nth(i).is_checked()
    # And all the rows should be selected
    rows = page.locator('.tabulator-row')
    for i in range(rows.count()):
        assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
    # The selection should have all the indexes
    wait_until(lambda: widget.selection == list(range(len(df_mixed))))


def test_tabulator_selection_selectable_checkbox_multiple(page, port, df_mixed):
    widget = Tabulator(df_mixed, selectable='checkbox')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    checkboxes = page.locator('input[type="checkbox"]')
    checkboxes.first.wait_for()
    checkboxes.nth(1).check()
    checkboxes.last.check()

    expected_selection = [0, len(df_mixed) - 1]

    for i in range(1, checkboxes.count()):
        if (i - 1) in expected_selection:
            assert checkboxes.nth(i).is_checked()
        else:
            assert not checkboxes.nth(i).is_checked()

    rows = page.locator('.tabulator-row')
    for i in range(rows.count()):
        if i in expected_selection:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')

    wait_until(lambda: widget.selection == expected_selection)


def test_tabulator_selection_selectable_checkbox_single(page, port, df_mixed):
    widget = Tabulator(df_mixed, selectable='checkbox-single')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    checkboxes = page.locator('input[type="checkbox"]')
    expect(checkboxes).to_have_count(len(df_mixed))
    checkboxes.first.check()
    checkboxes.last.check()

    expected_selection = [0, len(df_mixed) - 1]

    for i in range(checkboxes.count()):
        if i in expected_selection:
            assert checkboxes.nth(i).is_checked()
        else:
            assert not checkboxes.nth(i).is_checked()

    rows = page.locator('.tabulator-row')
    for i in range(rows.count()):
        if i in expected_selection:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')

    wait_until(lambda: widget.selection == expected_selection)


def test_tabulator_selection_selectable_toggle(page, port, df_mixed):
    widget = Tabulator(df_mixed, selectable='toggle')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    rows = page.locator('.tabulator-row')
    # Click on the first row of the index column to select the row
    c0 = page.locator('text="idx0"')
    c0.wait_for()
    c0.click()
    for i in range(rows.count()):
        if i == 0:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    assert wait_until(lambda: widget.selection == [0])
    # Click on the second row, the first row should still be selected
    page.locator('text="idx1"').click()
    for i in range(rows.count()):
        if i in [0, 1]:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    assert wait_until(lambda: widget.selection == [0, 1])
    # Click on a selected row deselect it
    page.locator('text="idx1"').click()
    for i in range(rows.count()):
        if i == 0:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    assert wait_until(lambda: widget.selection == [0])


def test_tabulator_selection_selectable_rows():
    pass
