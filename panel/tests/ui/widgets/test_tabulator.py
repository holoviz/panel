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
    pytestmark = pytest.mark.skip('playwright not available')

pytestmark = pytest.mark.ui

try:
    import numpy as np
except ImportError:
    pytestmark = pytest.mark.skip('numpy not available')

try:
    import pandas as pd
except ImportError:
    pytestmark = pytest.mark.skip('pandas not available')

from panel import state
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


def test_tabulator_show_index_disabled(page, port, df_mixed):
    widget = Tabulator(df_mixed, show_index=False)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('text="index"')).to_have_count(0)


def test_tabulator_titles(page, port, df_mixed):
    titles = {col: col.upper() for col in df_mixed.columns}
    widget = Tabulator(df_mixed, titles=titles)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    for col in df_mixed.columns:
        expected_title = titles[col]
        expect(page.locator(f'text="{expected_title}"')).to_have_count(1)


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


def test_tabulator_frozen_columns():
    pass


@pytest.mark.parametrize('theme', Tabulator.param['theme'].objects)
def test_tabulator_theming(page, port, df_mixed, theme):
    # Subscribe the reponse events to check that the CSS is loaded
    responses = []
    page.on("response", lambda response: responses.append(response))
    widget = Tabulator(df_mixed, theme=theme)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check that the whole table content is on the page
    table = page.locator('.bk.pnx-tabulator.tabulator')
    expect(table).to_have_text(
        'index\nint\nfloat\nstr\nbool\ndate\ndatetime\nidx0\n1\n3.14\nA\ntrue\n2019-01-01\n2019-01-01 10:00:00\nidx1\n2\n6.28\nB\ntrue\n2020-01-01\n2020-01-01 12:00:00\nidx2\n3\n9.42\nC\ntrue\n2020-01-10\n2020-01-10 13:00:00\nidx3\n4\n-2.45\nD\nfalse\n2019-01-10\n2020-01-15 13:00:00',  # noqa
        use_inner_text=True
    )
    found = False
    for response in responses:
        base = response.url.split('/')[-1]
        if base == f'tabulator_{theme}.min.css':
            found = True
            break
        # default theme
        elif base == 'tabulator.min.css':
            found = True
            break
    assert found
    assert response.status


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

    # This fails
    page.locator("text=group1 >> div").first.click(timeout=2000)

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
    wait_until(lambda: len(values) >= 1)
    assert values[-1] == ('index', 0, 'idx0')
    page.locator('text="A"').click()
    wait_until(lambda: len(values) >= 2)
    assert values[-1] == ('str', 0, 'A')


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

    wait_until(lambda: len(values) >= 1)
    assert values[0] == ('str', 0, 'A', 'AA')
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

    fltr, col = 'A', 'str'
    widget.add_filter(fltr, col)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(1)

    assert page.locator('text="A"').count() == 1
    assert page.locator('text="B"').count() == 0

    expected_current_view = df_mixed.loc[ df_mixed[col] == fltr, :]
    assert widget.current_view.equals(expected_current_view)


def test_tabulator_filter_constant_list(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    fltr, col = ['A', 'B'], 'str'
    widget.add_filter(fltr, col)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(2)

    assert page.locator('text="A"').count() == 1
    assert page.locator('text="B"').count() == 1
    assert page.locator('text="C"').count() == 0

    expected_current_view = df_mixed.loc[df_mixed[col].isin(fltr), :]
    assert widget.current_view.equals(expected_current_view)


def test_tabulator_filter_constant_tuple_range(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    fltr, col = (1, 2), 'int'
    widget.add_filter(fltr, col)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(2)

    assert page.locator('text="A"').count() == 1
    assert page.locator('text="B"').count() == 1
    assert page.locator('text="C"').count() == 0

    expected_current_view = df_mixed.loc[(df_mixed[col] >= fltr[0]) & (df_mixed[col] <= fltr[1]), : ]
    assert widget.current_view.equals(expected_current_view)


@pytest.mark.parametrize(
    'cols',
    [
        ['int', 'float', 'str', 'bool'],
        pytest.param(['date', 'datetime'], marks=pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3655')),
    ],
)
def test_tabulator_header_filters_default(page, port, df_mixed, cols):
    df_mixed = df_mixed[cols]
    widget = Tabulator(df_mixed, header_filters=True)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check that all the columns have a header filter, including the index column
    expect(page.locator('.tabulator-header-filter')).to_have_count(len(cols) + 1)

    # Check the table has the right number of rows, i.e. no filter is applied by default
    assert page.locator('.tabulator-row').count() == len(df_mixed)

    assert widget.filters == []
    assert widget.current_view.equals(df_mixed)


@pytest.mark.parametrize(
    ('index', 'expected_selector'),
    (
        (['idx0', 'idx1'], 'input[type="search"]'),
        ([0, 1], 'input[type="number"]'),
        (np.array([0, 1], dtype=np.uint64), 'input[type="number"]'),
        ([0.1, 1.1], 'input[type="number"]'),
        # ([True, False], 'input[type="checkbox"]'),  # Pandas cannot have boolean indexes apparently
    ),
)
def test_tabulator_header_filters_default_index(page, port, index, expected_selector):
    df = pd.DataFrame(index=index)
    widget = Tabulator(df, header_filters=True)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # The number columns (unit, int and float) are expected to have a number input
    expect(page.locator(expected_selector)).to_have_count(1)


def test_tabulator_header_filters_init_from_editors(page, port, df_mixed):
    df_mixed = df_mixed[['float']]
    editors = {
        'float': {'type': 'number', 'step': 0.5},
        'str': {'type': 'autocomplete', 'values': True}
    }
    widget = Tabulator(df_mixed, header_filters=True, editors=editors)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    number_header = page.locator('input[type="number"]')
    expect(number_header).to_have_count(1)
    assert number_header.get_attribute('step') == '0.5'


def test_tabulator_header_filters_init_explicitely(page, port, df_mixed):
    header_filters = {
        'float': {'type': 'number', 'func': '>=', 'placeholder': 'Placeholder float'},
        'str': {'type': 'input', 'func': 'like', 'placeholder': 'Placeholder str'},
    }
    widget = Tabulator(df_mixed, header_filters=header_filters)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check that only the columns explicitely given a header filter spec have a header filter
    expect(page.locator('.tabulator-header-filter')).to_have_count(len(header_filters))

    number_header = page.locator('input[type="number"]')
    expect(number_header).to_have_count(1)
    assert number_header.get_attribute('placeholder') == 'Placeholder float'
    str_header = page.locator('input[type="search"]')
    expect(str_header).to_have_count(1)
    assert str_header.get_attribute('placeholder') == 'Placeholder str'


def test_tabulator_header_filters_set_from_client(page, port, df_mixed):
    header_filters = {
        'float': {'type': 'number', 'func': '>=', 'placeholder': 'Placeholder float'},
        'str': {'type': 'input', 'func': 'like', 'placeholder': 'Placeholder str'},
    }
    widget = Tabulator(df_mixed, header_filters=header_filters)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    number_header = page.locator('input[type="number"]')
    number_header.click()
    val, cmp, col = '0', '>=', 'float'
    number_header.fill(val)
    number_header.press('Enter')
    query1 = f'{col} {cmp} {val}'
    expected_filter_df = df_mixed.query(query1)
    expected_filter1 = {'field': col, 'type': cmp, 'value': val}
    expect(page.locator('.tabulator-row')).to_have_count(len(expected_filter_df))
    wait_until(lambda: widget.filters == [expected_filter1])
    assert widget.current_view.equals(expected_filter_df)

    str_header = page.locator('input[type="search"]')
    str_header.click()
    val, cmp, col = 'A', 'like', 'str'
    str_header.fill(val)
    str_header.press('Enter')
    query2 = f'{col} == {val!r}'
    expected_filter_df = df_mixed.query(f'{query1} and {query2}')
    expected_filter2 = {'field': col, 'type': cmp, 'value': val}
    expect(page.locator('.tabulator-row')).to_have_count(len(expected_filter_df))
    wait_until(lambda: widget.filters == [expected_filter1, expected_filter2])
    assert widget.current_view.equals(expected_filter_df)


def test_tabulator_downloading():
    pass

def test_tabulator_streaming_default(page, port):
    df = pd.DataFrame(np.random.random((3, 2)), columns=['A', 'B'])
    widget = Tabulator(df)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('.tabulator-row')).to_have_count(len(df))

    height_start = page.locator('.bk.pnx-tabulator.tabulator').bounding_box()['height']


    def stream_data():
        widget.stream(df)  # follow is True by default

    repetitions = 3
    state.add_periodic_callback(stream_data, period=100, count=repetitions)

    expected_len = len(df) * (repetitions + 1)
    expect(page.locator('.tabulator-row')).to_have_count(expected_len)
    assert len(widget.value) == expected_len
    assert widget.current_view.equals(widget.value)

    assert page.locator('.bk.pnx-tabulator.tabulator').bounding_box()['height'] > height_start


def test_tabulator_streaming_no_follow(page, port):
    nrows1 = 10
    arr = np.random.randint(10, 20, (nrows1, 2))
    val = [-1]
    arr[0, :] = val[0]
    df = pd.DataFrame(arr, columns=['A', 'B'])
    widget = Tabulator(df, height=100)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('.tabulator-row')).to_have_count(len(df))
    assert page.locator('text="-1"').count() == 2

    height_start = page.locator('.bk.pnx-tabulator.tabulator').bounding_box()['height']

    recs = []
    nrows2 = 5
    def stream_data():
        arr = np.random.randint(10, 20, (nrows2, 2))
        val[0] = val[0] - 1
        arr[-1, :] = val[0]
        recs.append(val[0])
        new_df = pd.DataFrame(arr, columns=['A', 'B'])
        widget.stream(new_df, follow=False)

    repetitions = 3
    state.add_periodic_callback(stream_data, period=100, count=repetitions)

    # Explicit wait to make sure the periodic callback has completed
    page.wait_for_timeout(500)

    expect(page.locator('text="-1"')).to_have_count(2)
    # As we're not in follow mode the last row isn't visible
    # and seems to be out of reach to the selector. How visibility
    # is used here seems brittle though, may need to be revisited.
    expect(page.locator(f'text="{val[0]}"')).to_have_count(0)

    assert len(widget.value) == nrows1 + repetitions * nrows2
    assert widget.current_view.equals(widget.value)

    assert page.locator('.bk.pnx-tabulator.tabulator').bounding_box()['height'] == height_start


def test_tabulator_patching(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    new_vals = {
        'str': ['AA', 'BB'],
        'int': [100, 101],
    }

    widget.patch({
        'str': [(0, new_vals['str'][0]), (1, new_vals['str'][1])],
        'int': [(slice(0, 2), new_vals['int'])]
    }, as_index=False)

    for v in new_vals:
        expect(page.locator(f'text="{v}"')).to_have_count(1)

    assert list(widget.value['str'].iloc[[0, 1]]) == new_vals['str']
    assert list(widget.value['int'].iloc[0 : 2]) == new_vals['int']
    assert df_mixed.equals(widget.current_view)
    assert df_mixed.equals(widget.value)


def test_tabulator_patching_no_event(page, port, df_mixed):
    # Patching should not emit emit any event when watching `value`
    widget = Tabulator(df_mixed)

    events = []
    widget.param.watch(lambda e: events.append(e), 'value')

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    new_vals = {
        'str': ['AA', 'BB'],
    }

    widget.patch({
        'str': [(0, new_vals['str'][0]), (1, new_vals['str'][1])],
    }, as_index=False)

    for v in new_vals:
        expect(page.locator(f'text="{v}"')).to_have_count(1)

    assert list(widget.value['str'].iloc[[0, 1]]) == new_vals['str']
    assert df_mixed.equals(widget.value)

    assert len(events) == 0


def color_false(val):
    color = 'red' if not val else 'black'
    return 'color: %s' % color

def highlight_max(s):
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]

# Playwright returns the colors as RGB
_color_mapping = {
    'red': 'rgb(255, 0, 0)',
    'black': 'rgb(0, 0, 0)',
    'yellow': 'rgb(255, 255, 0)',
}

def test_tabulator_styling_init(page, port, df_mixed):
    df_styled = (
        df_mixed.style
        .apply(highlight_max, subset=['int'])
        .applymap(color_false, subset=['bool'])
    )
    widget = Tabulator(df_styled)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    max_int = df_mixed['int'].max()
    max_cell = page.locator('.tabulator-cell', has=page.locator(f'text="{max_int}"'))
    expect(max_cell).to_have_count(1)
    expect(max_cell).to_have_css('background-color', _color_mapping['yellow'])
    expect(page.locator('text="false"')).to_have_css('color', _color_mapping['red'])


def test_tabulator_patching_and_styling(page, port, df_mixed):
    df_styled = df_mixed.style.apply(highlight_max, subset=['int'])
    widget = Tabulator(df_styled)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Changing the highest value in the int column should
    # update the style so that this cell gets a yellow background
    widget.patch({'int': [(0, 100)]}, as_index=False)

    max_int = df_mixed['int'].max()
    max_cell = page.locator('.tabulator-cell', has=page.locator(f'text="{max_int}"'))
    expect(max_cell).to_have_count(1)
    expect(max_cell).to_have_css('background-color', _color_mapping['yellow'])


def test_tabulator_configuration(page, port, df_mixed):
    # By default the Tabulator widget has sortable columns.
    # Pass a configuration property to disable this behaviour.
    widget = Tabulator(df_mixed, configuration={'headerSort': False})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator(".tabulator-sortable")).to_have_count(0)


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3620')
def test_tabulator_editor_datetime_nan(page, port, df_mixed):
    df_mixed.at['idx0', 'datetime'] = np.nan
    widget = Tabulator(df_mixed, configuration={'headerSort': False})

    events = []
    def callback(e):
        events.append(e)

    widget.on_edit(callback)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Doesn't trigger a table edit event
    cell = page.locator('text="-"')
    cell.wait_for()
    cell.click()
    page.locator('input[type="date"]').press("Escape")

    # Error: these two triggers a table edit event, i.e. hit Enter
    # or click away
    page.locator('text="-"').click()
    page.locator('input[type="date"]').press("Enter")
    page.locator('text="-"').click()
    page.locator("html").click()

    wait_until(lambda: len(events) == 0)
