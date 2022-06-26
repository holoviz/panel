import datetime as dt
import sys
import time

import pytest

from bokeh.models.widgets.tables import (
    BooleanFormatter, DateFormatter, HTMLTemplateFormatter, NumberFormatter,
    ScientificFormatter, StringFormatter,
)

try:
    from playwright.sync_api import expect
except ImportError:
    pass

pytestmark = pytest.mark.ui

try:
    import numpy as np
except ImportError:
    pytestmark = pytest.mark.skip('numpy not available')

try:
    import pandas as pd
except ImportError:
    pytestmark = pytest.mark.skip('pandas not available')


from panel.io.server import serve
from panel.widgets import Tabulator


@pytest.fixture
def df_mixed():
    df = pd.DataFrame({
        'int': [1, 2, 3, 4],
        'float': [3.14, 6.28, 9.42, -2.45],
        'str': ['A', 'B', 'C', 'D'],
        'bool': [True, True, True, False],
        'date': [dt.date(2019, 1, 1), dt.date(2020, 1, 1), dt.date(2020, 1, 10), dt.date(2019, 1, 10)],
        'datetime': [dt.datetime(2019, 1, 1, 10), dt.datetime(2020, 1, 1, 12), dt.datetime(2020, 1, 10, 13), dt.datetime(2020, 1, 15, 13)]
    }, index=['idx0', 'idx1', 'idx2', 'idx3'])
    return df


@pytest.fixture
def df_multiindex(df_mixed):
    df_mi = df_mixed.copy()
    df_mi.index = pd.MultiIndex.from_tuples([
        ('group0', 'subgroup0'),
        ('group0', 'subgroup1'),
        ('group1', 'subgroup0'),
        ('group1', 'subgroup1'),
    ], names=['groups', 'subgroups'])
    return df_mi


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


def count_per_page(count: int, page_size: int):
    """
    >>> count_per_page(12, 7)
    [7, 5]
    """
    original_count = count
    count_per_page = []
    while True:
        page_count = min(count, page_size)
        count_per_page.append(page_count)
        count -= page_count
        if count == 0:
            break
    assert sum(count_per_page) == original_count
    return count_per_page


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
        'index\nint\nfloat\nstr\nbool\ndate\ndatetime\nidx0\n1\n3.14\nA\ntrue\n2019-01-01\n2019-01-01 10:00:00\nidx1\n2\n6.28\nB\ntrue\n2020-01-01\n2020-01-01 12:00:00\nidx2\n3\n9.42\nC\ntrue\n2020-01-10\n2020-01-10 13:00:00\nidx3\n4\n-2.45\nD\nfalse\n2019-01-10\n2020-01-15 13:00:00',  # noqa
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


def test_tabulator_value_changed(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    df_mixed.loc['idx0', 'str'] = 'AA'
    # Need to trigger the value as the dataframe was modified
    # in place which is not detected.
    widget.param.trigger('value')
    changed_cell = page.locator('text="AA"')
    expect(changed_cell).to_have_count(1)


def test_tabulator_disabled(page, port, df_mixed):
    widget = Tabulator(df_mixed, disabled=True)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    # If the cell was editable then this input element should
    # be found.
    expect(page.locator('input[type="text"]')).to_have_count(0)


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


def test_tabulator_formatters_bokeh_bool(page, port, df_mixed):
    s = [True] * len(df_mixed)
    s[-1] = False
    df_mixed['bool'] = s
    widget = Tabulator(df_mixed, formatters={'bool': BooleanFormatter()})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # The BooleanFormatter renders with svg icons.
    cells = page.locator(".tabulator-cell", has=page.locator("svg"))
    expect(cells).to_have_count(len(df_mixed))

    for i in range(len(df_mixed) - 1):
        assert cells.nth(i).get_attribute('aria-checked') == 'true'
    assert cells.last.get_attribute('aria-checked') == 'false'


def test_tabulator_formatters_bokeh_date(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        formatters={
            'date': DateFormatter(format='COOKIE'),
            'datetime': DateFormatter(format='%H:%M'),
        },
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="10:00"')).to_have_count(1)
    assert page.locator('text="Tue, 01 Jan 2019"').count() == 1


@pytest.mark.xfail(
    reason='NaNs not well handled by the DateFormatter with datetime.date objects.'
           ' See https://github.com/bokeh/bokeh/issues/12187'
)
def test_tabulator_formatters_bokeh_date_with_nan(page, port, df_mixed):
    df_mixed.loc['idx1', 'date'] = np.nan
    df_mixed.loc['idx1', 'datetime'] = np.nan
    widget = Tabulator(
        df_mixed,
        formatters={
            'date': DateFormatter(format='COOKIE', nan_format='nan-date'),
            'datetime': DateFormatter(format='%H:%M', nan_format= 'nan-datetime'),
        },
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="10:00"')).to_have_count(1)
    assert page.locator('text="Tue, 01 Jan 2019"').count() == 1  # This should fail
    assert page.locator('text="nan-date"').count() == 1
    assert page.locator('text="nan-datetime"').count() == 1


def test_tabulator_formatters_bokeh_number(page, port, df_mixed):
    df_mixed.loc['idx1', 'int'] = np.nan
    df_mixed.loc['idx1', 'float'] = np.nan
    widget = Tabulator(
        df_mixed,
        formatters={
            'int': NumberFormatter(format='0.000', nan_format='nan-int'),
            'float': NumberFormatter(format='0.000', nan_format='nan-float'),
        },
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="1.000"')).to_have_count(1)
    assert page.locator('text="3.140"').count() == 1
    assert page.locator('text="nan-int"').count() == 1
    assert page.locator('text="nan-float"').count() == 1


def test_tabulator_formatters_bokeh_string(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        formatters={
            'str': StringFormatter(font_style='bold', text_align='center', text_color='red'),
        },
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="A"')).to_have_attribute(
        "style",
        "font-weight: bold; text-align: center; color: rgb(255, 0, 0);"
    )


def test_tabulator_formatters_bokeh_html(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        formatters={
            'str': HTMLTemplateFormatter(template='<p style="font-weight: bold;"><%= value %></p>'),
        },
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="A"')).to_have_attribute(
        "style",
        "font-weight: bold;"
    )


def test_tabulator_formatters_bokeh_scientific(page, port, df_mixed):
    df_mixed['float'] = df_mixed['float'] * 1e6
    df_mixed.loc['idx1', 'float'] = np.nan
    widget = Tabulator(
        df_mixed,
        formatters={
            'float': ScientificFormatter(precision=3, nan_format='nan-float'),
        },
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="3.140e+6"')).to_have_count(1)
    assert page.locator('text="nan-float"').count() == 1


def test_tabulator_formatters_tabulator():
    pass


def test_tabulator_editors_bokeh():
    pass


def test_tabulator_editors_tabulator():
    pass


def test_tabulator_column_layouts():
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


def test_tabulator_selection_selectable_rows(page, port, df_mixed):
    widget = Tabulator(df_mixed, selectable_rows=lambda df: [1])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    rows = page.locator('.tabulator-row')
    # Click on the first row of the index column to select the row
    c1 = page.locator('text="idx1"')
    c1.wait_for()
    c1.click()
    assert wait_until(lambda: widget.selection == [1])
    # Click on the first row with CTRL pressed should add that row to the selection
    modifier = get_ctrl_modifier()
    page.locator("text=idx0").click(modifiers=[modifier])
    time.sleep(0.2)
    assert widget.selection == [1]
    for i in range(rows.count()):
        if i == 1:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')


def test_tabulator_selection_row_content(page, port, df_mixed):
    widget = Tabulator(df_mixed, row_content=lambda i: f"{i['str']}-row-content")

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    openables = page.locator('text="►"')
    expect(openables).to_have_count(len(df_mixed))

    expected_expanded = []
    for i in range(len(df_mixed)):
        openables = page.locator('text="►"')
        openables.first.click()
        row_content = page.locator(f'text="{df_mixed.iloc[i]["str"]}-row-content"')
        expect(row_content).to_have_count(1)
        closables = page.locator('text="▼"')
        expect(closables).to_have_count(i + 1)
        assert row_content.is_visible()
        expected_expanded.append(i)
        wait_until(lambda: widget.expanded == expected_expanded)

    for i in range(len(df_mixed)):
        closables = page.locator('text="▼"')
        closables.first.click()
        row_content = page.locator(f'text="{df_mixed.iloc[i]["str"]}-row-content"')
        expect(row_content).to_have_count(0)  # timeout here?
        expected_expanded.remove(i)
        wait_until(lambda: widget.expanded == expected_expanded)


def test_tabulator_selection_row_content_expand_from_python_init(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        row_content=lambda i: f"{i['str']}-row-content",
        expanded = [0, 2],
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    for i in range(len(df_mixed)):
        row_content = page.locator(f'text="{df_mixed.iloc[i]["str"]}-row-content"')
        if i in widget.expanded:
            expect(row_content).to_have_count(1)
        else:
            expect(row_content).to_have_count(0)

    openables = page.locator('text="►"')
    closables = page.locator('text="▼"')
    assert closables.count() == len(widget.expanded)
    assert openables.count() == len(df_mixed) - len(widget.expanded)


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3646')
def test_tabulator_selection_row_content_expand_from_python_after(page, port, df_mixed):
    widget = Tabulator(df_mixed, row_content=lambda i: f"{i['str']}-row-content")

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Expanding the rows after the server is launched
    widget.expanded = [0, 2]

    for i in range(len(df_mixed)):
        row_content = page.locator(f'text="{df_mixed.iloc[i]["str"]}-row-content"')
        if i in widget.expanded:
            expect(row_content).to_have_count(1)
        else:
            expect(row_content).to_have_count(0)

    openables = page.locator('text="►"')
    closables = page.locator('text="▼"')
    # Error here
    assert closables.count() == len(widget.expanded)
    assert openables.count() == len(df_mixed) - len(widget.expanded)
    # End of error

    widget.expanded = []

    openables = page.locator('text="►"')
    closables = page.locator('text="▼"')
    assert closables.count() == 0
    assert openables.count() == len(df_mixed)


def test_tabulator_grouping():
    pass


def test_tabulator_groupby():
    pass


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3564')
def test_tabulator_hierarchical(page, port, df_multiindex):
    widget = Tabulator(df_multiindex, hierarchical=True)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="Index: groups | subgroups"')).to_have_count(1)

    for i in range(len(df_multiindex.index.get_level_values(0).unique())):
        gr = page.locator(f'text="group{i}"')
        expect(gr).to_have_count(1)
        assert gr.is_visible()
    for i in range(len(df_multiindex.index.get_level_values(1).unique())):
        subgr = page.locator(f'text="subgroup{i}"')
        expect(subgr).to_have_count(0)

    page.locator("text=group1 >> div").first.click()

    for i in range(len(df_multiindex.index.get_level_values(1).unique())):
        subgr = page.locator(f'text="subgroup{i}"')
        expect(subgr).to_have_count(1)
        assert subgr.is_visible()


def test_tabulator_cell_click_event(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    values = []
    widget.on_click(lambda e: values.append((e.column, e.row, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.locator('text="idx0"').click()
    wait_until(lambda: values[0] == ('index', 0, 'idx0'))
    page.locator('text="A"').click()
    wait_until(lambda: values[0] == ('str', 0, 'A'))


def test_tabulator_edit_event(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("AA")
    editable_cell.press('Enter')

    wait_until(lambda: values[0] == ('str', 0, 'A', 'AA'))
    assert df_mixed.at['idx0', 'str'] == 'AA'

@pytest.mark.parametrize(
    'pagination',
    [
        'remote',
        pytest.param('local', marks=pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3647')),
    ],
)
def test_tabulator_pagination(page, port, df_mixed, pagination):
    page_size = 2
    widget = Tabulator(df_mixed, pagination=pagination, page_size=page_size)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    counts = count_per_page(len(df_mixed), page_size)
    i = 0
    while True:
        wait_until(lambda: widget.page == i + 1)
        rows = page.locator('.tabulator-row')
        expect(rows).to_have_count(counts[i])
        assert page.locator(f'[aria-label="Show Page {i+1}"]').count() == 1
        df_page = df_mixed.iloc[i * page_size: (i + 1) * page_size]
        for idx in df_page.index:
            assert page.locator(f'text="{idx}"').count() == 1
        if i < len(counts) - 1:
            page.locator(f'[aria-label="Show Page {i+2}"]').click()
            i += 1
        else:
            break


def test_tabulator_filter_constant_scalar(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    widget.add_filter('A', 'str')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(1)

    assert page.locator('text="A"').count() == 1
    assert page.locator('text="B"').count() == 0


def test_tabulator_filter_constant_list(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    widget.add_filter(['A', 'B'], 'str')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(2)

    assert page.locator('text="A"').count() == 1
    assert page.locator('text="B"').count() == 1
    assert page.locator('text="C"').count() == 0


def test_tabulator_filter_constant_tuple_range(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    widget.add_filter((1, 2), 'int')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(2)

    assert page.locator('text="A"').count() == 1
    assert page.locator('text="B"').count() == 1
    assert page.locator('text="C"').count() == 0
