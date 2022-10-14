from __future__ import annotations

import datetime as dt
import time

import param
import pytest

from bokeh.models.widgets.tables import (
    BooleanFormatter, CheckboxEditor, DateEditor, DateFormatter,
    HTMLTemplateFormatter, IntEditor, NumberEditor, NumberFormatter,
    ScientificFormatter, SelectEditor, StringEditor, StringFormatter,
    TextEditor,
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
from panel.depends import bind
from panel.io.server import serve
from panel.models.tabulator import _TABULATOR_THEMES_MAPPING
from panel.tests.util import get_ctrl_modifier, wait_until
from panel.widgets import Select, Tabulator


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


@pytest.fixture(scope='session')
def df_mixed_as_string():
    return """
        index
        int
        float
        str
        bool
        date
        datetime
        idx0
        1
        3.14
        A
        true
        2019-01-01
        2019-01-01 10:00:00
        idx1
        2
        6.28
        B
        true
        2020-01-01
        2020-01-01 12:00:00
        idx2
        3
        9.42
        C
        true
        2020-01-10
        2020-01-10 13:00:00
        idx3
        4
        -2.45
        D
        false
        2019-01-10
        2020-01-15 13:00:00
    """


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


def tabulator_column_values(page, col_name: str) -> list[str]:
    """Get the values of a column.

    >>> tabulator_column_values(page, 'color')
    ['blue', 'red']
    """
    cells = page.locator(f'[tabulator-field={col_name}][role=gridcell]')
    return cells.all_inner_texts()


def test_tabulator_no_console_error(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    msgs = []
    page.on("console", lambda msg: msgs.append(msg))

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    time.sleep(1)

    assert [msg for msg in msgs if msg.type == 'error' and 'favicon' not in msg.location['url']] == []


def test_tabulator_default(page, port, df_mixed, df_mixed_as_string):
    nrows, ncols = df_mixed.shape
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_ncols = ncols + 2  # _index + index + data columns

    # Check that the whole table content is on the page
    table = page.locator('.bk.pnx-tabulator.tabulator')
    expect(table).to_have_text(
        df_mixed_as_string,
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


def test_tabulator_hidden_columns(page, port, df_mixed):
    widget = Tabulator(df_mixed, hidden_columns=['float', 'date', 'datetime'])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_text = """
        index
        int
        str
        bool
        idx0
        1
        A
        true
        idx1
        2
        B
        true
        idx2
        3
        C
        true
        idx3
        4
        D
        false
    """
    # Check that the whole table content is on the page
    table = page.locator('.bk.pnx-tabulator.tabulator')
    expect(table).to_have_text(expected_text, use_inner_text=True)


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

    time.sleep(0.2)

    assert state == expected_state
    wait_until(lambda: state == expected_state, page)


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


def test_tabulator_formatters_tabulator_str(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        formatters={'int': 'star'},
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # The star formatter renders with svg icons.
    cells = page.locator(".tabulator-cell", has=page.locator("svg"))
    expect(cells).to_have_count(len(df_mixed))


def test_tabulator_formatters_tabulator_dict(page, port, df_mixed):
    nstars = 10
    widget = Tabulator(
        df_mixed,
        formatters={'int': {'type': 'star', 'stars': nstars}},
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # The star formatter renders with svg icons.
    cells = page.locator(".tabulator-cell", has=page.locator("svg"))
    expect(cells).to_have_count(len(df_mixed))

    stars = page.locator('svg')
    assert stars.count() == len(df_mixed) * nstars


def test_tabulator_formatters_after_init(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Wait until the table is rendered
    expect(page.locator('.tabulator-row')).to_have_count(len(df_mixed))

    # Formatters can be set after initialization, the table should be
    # updated accordingly
    widget.formatters = {
        'str': HTMLTemplateFormatter(template='<p style="font-weight: bold;"><%= value %></p>'),
    }

    expect(page.locator('text="A"')).to_have_attribute(
        "style",
        "font-weight: bold;"
    )


def test_tabulator_editors_bokeh_string(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'str': StringEditor()})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    # A StringEditor is turned into an input text tabulator editor
    expect(page.locator('input[type="text"]')).to_have_count(1)


def test_tabulator_editors_bokeh_string_completions(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'str': StringEditor(completions=['AAA'])})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    # A StringEditor with completions is turned into an autocomplete
    # tabulator editor.
    expect(page.locator('text="AAA"')).to_have_count(1)


def test_tabulator_editors_bokeh_text(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'str': TextEditor()})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    # A TextEditor with completions is turned into a textarea
    # tabulator editor.
    expect(page.locator('textarea')).to_have_count(1)


def test_tabulator_editors_bokeh_int(page, port, df_mixed):
    step = 2
    widget = Tabulator(df_mixed, editors={'int': IntEditor(step=step)})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="1" >> visible=true')
    cell.click()
    # An IntEditor with step is turned into a number tabulator editor
    # with step respected
    input = page.locator('input[type="number"]')
    expect(input).to_have_count(1)
    assert int(input.get_attribute('step')) == step


def test_tabulator_editors_bokeh_number(page, port, df_mixed):
    step = 0.1
    widget = Tabulator(df_mixed, editors={'float': NumberEditor(step=step)})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="3.14"')
    cell.click()
    # A NumberEditor with step is turned into a number tabulator editor
    # with step respected
    input = page.locator('input[type="number"]')
    expect(input).to_have_count(1)
    assert input.get_attribute('step') == str(step)


def test_tabulator_editors_bokeh_checkbox(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'bool': CheckboxEditor()})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="true"').first
    cell.click()
    # A CheckboxEditor is turned into a tickCross tabulator editor
    input = page.locator('input[type="checkbox"]')
    expect(input).to_have_count(1)
    assert input.get_attribute('value') == "true"


def test_tabulator_editors_bokeh_date(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'date': DateEditor()})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="2019-01-01"')
    cell.click()
    # A DateEditor is turned into a Panel date editor
    expect(page.locator('input[type="date"]')).to_have_count(1)


def test_tabulator_editors_bokeh_select(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'str': SelectEditor(options=['option1'])})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    # A SelectEditor with options is turned into a select tabulator editor.
    expect(page.locator('text="option1"')).to_have_count(1)


def test_tabulator_editors_panel_date(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'date': 'date'})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="2019-01-01"')
    cell.click()
    # A date editor is turned into an date input
    cell_edit = page.locator('input[type="date"]')
    new_date = "1980-01-01"
    cell_edit.fill(new_date)
    # Need to Enter to validate the change
    page.locator('input[type="date"]').press('Enter')
    expect(page.locator(f'text="{new_date}"')).to_have_count(1)
    new_date = dt.datetime.strptime(new_date, '%Y-%m-%d').date()
    assert new_date in widget.value['date'].tolist()

    cell = page.locator(f'text="{new_date}"')
    cell.click()
    cell_edit = page.locator('input[type="date"]')
    new_date2 = "1990-01-01"
    cell_edit.fill(new_date2)
    # Escape invalidates the change
    page.locator('input[type="date"]').press('Escape')
    expect(page.locator(f'text="{new_date2}"')).to_have_count(0)
    new_date2 = dt.datetime.strptime(new_date2, '%Y-%m-%d').date()
    assert new_date2 not in widget.value['date'].tolist()


def test_tabulator_editors_panel_datetime(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'datetime': 'datetime'})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="2019-01-01 10:00:00"')
    cell.click()
    # A date editor is turned into an date input
    cell_edit = page.locator('input[type="datetime-local"]')
    new_datetime = dt.datetime(1980, 11, 30, 4, 51, 0)
    time_to_fill = new_datetime.isoformat()
    # Somehow the seconds don't seem to be handled by datetime-local
    time_to_fill = time_to_fill[:-3]
    cell_edit.fill(time_to_fill)
    # Need to Enter to validate the change
    page.locator('input[type="datetime-local"]').press('Enter')
    new_datetime_display = new_datetime.strftime('%Y-%m-%d %H:%M:%S')
    expect(page.locator(f'text="{new_datetime_display}"')).to_have_count(1)
    assert new_datetime in widget.value['datetime'].tolist()

    cell = page.locator(f'text="{new_datetime_display}"')
    cell.click()
    cell_edit = page.locator('input[type="datetime-local"]')
    new_datetime2 = dt.datetime(1990, 3, 31, 12, 45, 0)
    time_to_fill2 = new_datetime2.isoformat()
    time_to_fill2 = time_to_fill2[:-3]
    cell_edit.fill(time_to_fill2)
    # Escape invalidates the change
    page.locator('input[type="datetime-local"]').press('Escape')
    new_datetime_display2 = new_datetime2.strftime('%Y-%m-%d %H:%M:%S')
    expect(page.locator(f'text="{new_datetime_display2}"')).to_have_count(0)
    assert new_datetime2 not in widget.value['datetime'].tolist()


def test_tabulator_editors_tabulator_disable_one(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        editors={'float': None},
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.locator('text="3.14"').click()
    page.wait_for_timeout(200)
    expect(page.locator('input[type="number"]')).to_have_count(0)


def test_tabulator_editors_tabulator_str(page, port, df_mixed):
    widget = Tabulator(df_mixed, editors={'str': 'textarea'})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    expect(page.locator('textarea')).to_have_count(1)


def test_tabulator_editors_tabulator_dict(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        editors={'str': {'type': 'textarea', 'elementAttributes': {'maxlength': '10'}}}
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="A"')
    cell.click()
    textarea = page.locator('textarea')
    expect(textarea).to_have_count(1)
    assert textarea.get_attribute('maxlength') == "10"


def test_tabulator_editors_tabulator_list_default(page, port):
    df = pd.DataFrame({'values': ['A', 'B']})
    widget = Tabulator(df, header_filters={'values': 'list'})

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    header = page.locator('input[type="search"]')
    expect(header).to_have_count(1)
    header.click()

    # There should be a select element with the list of unique values
    # found in the column.
    expect(page.locator('.tabulator-edit-list')).to_have_text('AB')


@pytest.mark.parametrize('layout', Tabulator.param['layout'].objects)
def test_tabulator_column_layouts(page, port, df_mixed, layout):
    widget = Tabulator(df_mixed, layout=layout)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    layout_mapping = {
        "fit_data": "fitData",
        "fit_data_fill": "fitDataFill",
        "fit_data_stretch": "fitDataStretch",
        "fit_data_table": "fitDataTable",
        "fit_columns": "fitColumns",
    }

    expected_layout = layout_mapping[layout]

    expect(page.locator('.pnx-tabulator')).to_have_attribute('tabulator-layout', expected_layout)


def test_tabulator_alignment_header_default(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # The default header alignment is left
    for col in df_mixed.columns:
        expect(page.locator(f'text="{col}"')).to_have_css('text-align', 'left')


def test_tabulator_alignment_text_default(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    findex = df_mixed.index[0]
    cell = page.locator(f'text="{findex}"')
    # Indexes are left aligned
    expect(cell).to_have_css('text-align', 'left')

    val = df_mixed.at[findex, 'int']
    # Selecting the visible 1 as there's a non displayed 1 in the hidden index
    cell = page.locator(f'text="{val}" >> visible=true')
    # Integers are right aligned
    expect(cell).to_have_css('text-align', 'right')

    val = df_mixed.at[findex, 'float']
    cell = page.locator(f'text="{val}"')
    # Floats are right aligned
    expect(cell).to_have_css('text-align', 'right')

    val = df_mixed.at[findex, 'bool']
    val = 'true' if val else 'false'
    cell = page.locator(f'text="{val}"').first
    # Booleans are centered
    expect(cell).to_have_css('text-align', 'center')

    val = df_mixed.at[findex, 'datetime']
    val = val.strftime('%Y-%m-%d %H:%M:%S')
    cell = page.locator(f'text="{val}"')
    # Datetimes are right aligned
    expect(cell).to_have_css('text-align', 'right')

    val = df_mixed.at[findex, 'str']
    cell = page.locator(f'text="{val}"')
    # Other types are left aligned
    expect(cell).to_have_css('text-align', 'left')


def test_tabulator_alignment_header_str(page, port, df_mixed):
    halign = 'center'
    widget = Tabulator(df_mixed, header_align=halign)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    for col in df_mixed.columns:
        expect(page.locator(f'text="{col}"')).to_have_css('text-align', halign)


def test_tabulator_alignment_header_dict(page, port, df_mixed):
    halign = {'int': 'left'}
    widget = Tabulator(df_mixed, header_align=halign)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # for col in df_mixed.columns:
    for col, align in halign.items():
        expect(page.locator(f'text="{col}"')).to_have_css('text-align', align)


def test_tabulator_alignment_text_str(page, port, df_mixed):
    talign = 'center'
    widget = Tabulator(df_mixed, text_align=talign)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cells = page.locator('.tabulator-cell:visible')

    expect(cells).to_have_count(len(df_mixed) * (df_mixed.shape[1] + 1))

    for i in range(cells.count()):
        expect(cells.nth(i)).to_have_css('text-align', talign)


def test_tabulator_frozen_columns(page, port, df_mixed):
    widths = 100
    width = int(((df_mixed.shape[1] + 1) * widths) / 2)
    frozen_cols = ['float', 'int']
    widget = Tabulator(df_mixed, frozen_columns=frozen_cols, width=width, widths=widths)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_text = """
    float
    int
    index
    str
    bool
    date
    datetime
    3.14
    1
    idx0
    A
    true
    2019-01-01
    2019-01-01 10:00:00
    6.28
    2
    idx1
    B
    true
    2020-01-01
    2020-01-01 12:00:00
    9.42
    3
    idx2
    C
    true
    2020-01-10
    2020-01-10 13:00:00
    -2.45
    4
    idx3
    D
    false
    2019-01-10
    2020-01-15 13:00:00
    """
    # Check that the whole table content is on the page, it is not in the
    # same order as if the table was displayed without frozen columns
    table = page.locator('.bk.pnx-tabulator.tabulator')
    expect(table).to_have_text(
        expected_text,
        use_inner_text=True
    )

    float_bb = page.locator('text="float"').bounding_box()
    int_bb = page.locator('text="int"').bounding_box()
    bool_bb = page.locator('text="bool"').bounding_box()

    # Check that the float column is rendered before the int column
    assert float_bb['x'] < int_bb['x']

    # Scroll to the right, and give it a little extra time
    page.locator('text="2019-01-01 10:00:00"').scroll_into_view_if_needed()
    page.wait_for_timeout(200)

    # Check that the two frozen columns haven't moved after scrolling right
    assert float_bb == page.locator('text="float"').bounding_box()
    assert int_bb == page.locator('text="int"').bounding_box()
    # But check that the position of one of the non frozen columns has indeed moved
    assert bool_bb['x'] > page.locator('text="bool"').bounding_box()['x']


def test_tabulator_frozen_rows(page, port):
    arr = np.array(['a'] * 10)

    arr[1] = 'X'
    arr[-2] = 'Y'
    arr[-1] = 'T'
    df = pd.DataFrame({'col': arr})
    height, width = 200, 200
    widget = Tabulator(df, frozen_rows=[-2, 1], height=height, width=width)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_text = """
    index
    col
    8
    Y
    1
    X
    0
    a
    2
    a
    3
    a
    4
    a
    5
    a
    6
    a
    7
    a
    9
    T
    """

    expect(page.locator('.tabulator')).to_have_text(
        expected_text,
        use_inner_text=True
    )

    X_bb = page.locator('text="X"').bounding_box()
    Y_bb = page.locator('text="Y"').bounding_box()

    # Check that the Y row is rendered before the X column
    assert Y_bb['y'] < X_bb['y']

    # Scroll to the bottom, and give it a little extra time
    page.locator('text="T"').scroll_into_view_if_needed()
    page.wait_for_timeout(200)

    # Check that the two frozen columns haven't moved after scrolling right
    assert X_bb == page.locator('text="X"').bounding_box()
    assert Y_bb == page.locator('text="Y"').bounding_box()


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3669')
def test_tabulator_patch_no_horizontal_rescroll(page, port, df_mixed):
    widths = 100
    width = int(((df_mixed.shape[1] + 1) * widths) / 2)
    df_mixed['tomodify'] = 'target'
    widget = Tabulator(df_mixed, width=width, widths=widths)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="target"').first
    # Scroll to the right
    cell.scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    bb = page.locator('text="tomodify"').bounding_box()
    # Patch a cell in the latest column
    widget.patch({'tomodify': [(0, 'target-modified')]}, as_index=False)

    # Catch a potential rescroll
    page.wait_for_timeout(400)
    # The table should keep the same scroll position
    # This fails
    assert bb == page.locator('text="tomodify"').bounding_box()


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3249')
def test_tabulator_patch_no_vertical_rescroll(page, port):
    size = 10
    arr = np.random.choice(list('abcd'), size=size)

    target, new_val = 'X', 'Y'
    arr[-1] = target
    df = pd.DataFrame({'col': arr})
    height, width = 100, 200
    widget = Tabulator(df, height=height, width=width)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Scroll to the bottom
    target_cell = page.locator(f'text="{target}"')
    target_cell.scroll_into_view_if_needed()
    page.wait_for_timeout(400)
    # Unfortunately that doesn't scroll down quite enough, it's missing
    # a little scroll down so we do it manually which is more brittle.
    # Might be a little brittle, setting the mouse somewhere in the table
    # and scroll down
    page.mouse.move(x=int(width/2), y=int(height/2))
    page.mouse.wheel(delta_x=0, delta_y=10000)
    # Give it time to scroll
    page.wait_for_timeout(400)

    bb = page.locator(f'text="{target}"').bounding_box()
    # Patch a cell in the latest row
    widget.patch({'col': [(size-1, new_val)]})

    # Wait to catch a potential rescroll
    page.wait_for_timeout(400)
    # The table should keep the same scroll position
    # This fails
    assert bb == page.locator(f'text="{new_val}"').bounding_box()


@pytest.mark.parametrize(
    'pagination',
    (
        pytest.param('local', marks=pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3553')),
        pytest.param('remote', marks=pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3553')),
        None,
    )
)
def test_tabulator_header_filter_no_horizontal_rescroll(page, port, df_mixed, pagination):
    widths = 100
    width = int(((df_mixed.shape[1] + 1) * widths) / 2)
    col_name = 'newcol'
    df_mixed[col_name] = 'on'
    widget = Tabulator(
        df_mixed,
        width=width,
        widths=widths,
        header_filters={col_name: {'type': 'input', 'func': 'like'}},
        pagination=pagination
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    header = page.locator(f'text="{col_name}"')
    # Scroll to the right
    header.scroll_into_view_if_needed()
    bb = header.bounding_box()

    header = page.locator('input[type="search"]')
    header.click()
    header.fill('off')
    header.press('Enter')

    # Wait to catch a potential rescroll
    page.wait_for_timeout(400)
    header = page.locator(f'text="{col_name}"')
    header.wait_for()
    # The table should keep the same scroll position, this fails
    assert bb == header.bounding_box()
    # assert bb == page.locator(f'text="{col_name}"').bounding_box()


def test_tabulator_header_filter_always_visible(page, port, df_mixed):
    col_name = 'newcol'
    df_mixed[col_name] = 'on'
    widget = Tabulator(
        df_mixed,
        header_filters={col_name: {'type': 'input', 'func': 'like'}},
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    header = page.locator('input[type="search"]')
    expect(header).to_have_count(1)
    header.click()
    header.fill('off')
    header.press('Enter')

    wait_until(lambda: widget.current_view.empty, page)

    header = page.locator('input[type="search"]')
    expect(header).to_have_count(1)


@pytest.mark.parametrize('theme', Tabulator.param['theme'].objects)
def test_tabulator_theming(page, port, df_mixed, df_mixed_as_string, theme):
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
        df_mixed_as_string,
        use_inner_text=True
    )
    found = False
    theme = _TABULATOR_THEMES_MAPPING.get(theme, theme)
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
    wait_until(lambda: widget.selection == [0], page)
    assert 'tabulator-selected' in rows.first.get_attribute('class')
    for i in range(1, rows.count()):
        assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    expected_selected = df_mixed.loc[['idx0'], :]
    assert widget.selected_dataframe.equals(expected_selected)


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
    wait_until(lambda: widget.selection == [0], page)
    expected_selected = df_mixed.loc[['idx0'], :]
    assert widget.selected_dataframe.equals(expected_selected)
    # Click on the second row should deselect the first one
    page.locator('text="idx1"').click()
    wait_until(lambda: widget.selection == [1], page)
    expected_selected = df_mixed.loc[['idx1'], :]
    assert widget.selected_dataframe.equals(expected_selected)
    for i in range(rows.count()):
        if i == 1:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    # Clicking again on the second row should not change anything
    page.locator('text="idx1"').click()
    wait_until(lambda: widget.selection == [1], page)
    assert widget.selected_dataframe.equals(expected_selected)
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
    wait_until(lambda: widget.selection == expected_selection, page)
    expected_selected = df_mixed.loc[['idx0', 'idx2'], :]
    assert widget.selected_dataframe.equals(expected_selected)
    for i in range(rows.count()):
        if i in expected_selection:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    # Clicking again on the third row with CTRL pressed should remove the row from the selection
    page.locator("text=idx2").click(modifiers=[modifier])
    expected_selection = [0]
    wait_until(lambda: widget.selection == expected_selection, page)
    expected_selected = df_mixed.loc[['idx0'], :]
    assert widget.selected_dataframe.equals(expected_selected)
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
    wait_until(lambda: widget.selection == expected_selection, page)
    expected_selected = df_mixed.loc['idx0':'idx2', :]
    assert widget.selected_dataframe.equals(expected_selected)
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
    page.wait_for_timeout(200)
    assert widget.selection == []
    assert widget.selected_dataframe.empty
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
    expected_selected = df_mixed.loc[['idx0', 'idx2'], :]
    assert widget.selected_dataframe.equals(expected_selected)


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
    wait_until(lambda: widget.selection == list(range(len(df_mixed))), page)
    assert widget.selected_dataframe.equals(df_mixed)


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

    wait_until(lambda: widget.selection == expected_selection, page)
    expected_selected = df_mixed.iloc[expected_selection, :]
    assert widget.selected_dataframe.equals(expected_selected)


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

    wait_until(lambda: widget.selection == expected_selection, page)
    expected_selected = df_mixed.iloc[expected_selection, :]
    assert widget.selected_dataframe.equals(expected_selected)


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
    wait_until(lambda: widget.selection == [0], page)
    expected_selected = df_mixed.loc[['idx0'], :]
    assert widget.selected_dataframe.equals(expected_selected)
    # Click on the second row, the first row should still be selected
    page.locator('text="idx1"').click()
    for i in range(rows.count()):
        if i in [0, 1]:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    wait_until(lambda: widget.selection == [0, 1], page)
    expected_selected = df_mixed.loc[['idx0', 'idx1'], :]
    assert widget.selected_dataframe.equals(expected_selected)
    # Click on a selected row deselect it
    page.locator('text="idx1"').click()
    for i in range(rows.count()):
        if i == 0:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    wait_until(lambda: widget.selection == [0], page)
    expected_selected = df_mixed.loc[['idx0'], :]
    assert widget.selected_dataframe.equals(expected_selected)


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
    wait_until(lambda: widget.selection == [1], page)
    expected_selected = df_mixed.loc[['idx1'], :]
    assert widget.selected_dataframe.equals(expected_selected)
    # Click on the first row with CTRL pressed should NOT add that row to the selection
    # as this row is not selectable
    modifier = get_ctrl_modifier()
    page.locator("text=idx0").click(modifiers=[modifier])
    page.wait_for_timeout(200)
    assert widget.selection == [1]
    for i in range(rows.count()):
        if i == 1:
            assert 'tabulator-selected' in rows.nth(i).get_attribute('class')
        else:
            assert 'tabulator-selected' not in rows.nth(i).get_attribute('class')
    assert widget.selected_dataframe.equals(expected_selected)


@pytest.mark.flaky(max_runs=3)
def test_tabulator_row_content(page, port, df_mixed):
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
        wait_until(lambda: widget.expanded == expected_expanded, page)

    for i in range(len(df_mixed)):
        closables = page.locator('text="▼"')
        closables.first.click()
        row_content = page.locator(f'text="{df_mixed.iloc[i]["str"]}-row-content"')
        expect(row_content).to_have_count(0)  # timeout here?
        expected_expanded.remove(i)
        wait_until(lambda: widget.expanded == expected_expanded, page)


def test_tabulator_row_content_expand_from_python_init(page, port, df_mixed):
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


def test_tabulator_row_content_expand_from_python_after(page, port, df_mixed):
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


def test_tabulator_groups(page, port, df_mixed):
    widget = Tabulator(
        df_mixed,
        groups={'Group1': ['int', 'float'], 'Group2': ['date', 'datetime']},
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_text = """
    index
    Group1
    int
    float
    str
    bool
    Group2
    date
    datetime
    idx0
    1
    3.14
    A
    true
    2019-01-01
    2019-01-01 10:00:00
    idx1
    2
    6.28
    B
    true
    2020-01-01
    2020-01-01 12:00:00
    idx2
    3
    9.42
    C
    true
    2020-01-10
    2020-01-10 13:00:00
    idx3
    4
    -2.45
    D
    false
    2019-01-10
    2020-01-15 13:00:00
    """

    expect(page.locator('.tabulator')).to_have_text(
        expected_text,
        use_inner_text=True,
    )

    expect(page.locator('.tabulator-col-group')).to_have_count(2)


def test_tabulator_groupby(page, port):
    df = pd.DataFrame({
        'cat1': ['A', 'B', 'A', 'A', 'B', 'B', 'B'],
        'cat2': ['X', 'X', 'X', 'X', 'Y', 'Y', 'Y'],
        'value': list(range(7)),
    })

    widget = Tabulator(df, groupby=['cat1', 'cat2'])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_text = """
    index
    cat1
    cat2
    value
    cat1: A, cat2: X(3 items)
    0
    A
    X
    0
    2
    A
    X
    2
    3
    A
    X
    3
    cat1: B, cat2: X(1 item)
    1
    B
    X
    1
    cat1: B, cat2: Y(3 items)
    4
    B
    Y
    4
    5
    B
    Y
    5
    6
    B
    Y
    6
    """

    expect(page.locator('.tabulator')).to_have_text(
        expected_text,
        use_inner_text=True,
    )

    expect(page.locator('.tabulator-group')).to_have_count(3)


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
    wait_until(lambda: len(values) >= 1, page)
    assert values[-1] == ('index', 0, 'idx0')
    page.locator('text="A"').click()
    wait_until(lambda: len(values) >= 2, page)
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

    wait_until(lambda: len(values) >= 1, page)
    assert values[0] == ('str', 0, 'A', 'AA')
    assert df_mixed.at['idx0', 'str'] == 'AA'


@pytest.mark.parametrize('pagination', ['remote', 'local'])
def test_tabulator_pagination(page, port, df_mixed, pagination):
    page_size = 2
    widget = Tabulator(df_mixed, pagination=pagination, page_size=page_size)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    counts = count_per_page(len(df_mixed), page_size)
    i = 0
    while True:
        wait_until(lambda: widget.page == i + 1, page)
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


def test_tabulator_filter_param(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    class P(param.Parameterized):
        s = param.String()

    filt_val, filt_col = 'A', 'str'
    p = P(s=filt_val)
    widget.add_filter(p.param['s'], column=filt_col)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    df_filtered = df_mixed.loc[df_mixed[filt_col] == filt_val, :]

    wait_until(lambda: widget.current_view.equals(df_filtered), page)

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(len(df_filtered))

    for filt_val in ['B', 'NOT']:
        p.s = filt_val
        page.wait_for_timeout(200)
        df_filtered = df_mixed.loc[df_mixed[filt_col] == filt_val, :]

        wait_until(lambda: widget.current_view.equals(df_filtered), page)

        # Check the table has the right number of rows
        expect(page.locator('.tabulator-row')).to_have_count(len(df_filtered))


def test_tabulator_filter_bound_function(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    def filt_(df, val):
        return df[df['str'] == val]

    filt_val = 'A'
    w_filter = Select(value='A', options=['A', 'B', ''])
    widget.add_filter(bind(filt_, val=w_filter))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    df_filtered = filt_(df_mixed, w_filter.value)

    wait_until(lambda: widget.current_view.equals(df_filtered), page)

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(len(df_filtered))

    for filt_val in w_filter.options[1:]:
        w_filter.value = filt_val
        page.wait_for_timeout(200)
        df_filtered = filt_(df_mixed, filt_val)

        wait_until(lambda: widget.current_view.equals(df_filtered), page)

        # Check the table has the right number of rows
        expect(page.locator('.tabulator-row')).to_have_count(len(df_filtered))


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


def test_tabulator_header_filters_init_explicitly(page, port, df_mixed):
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
    wait_until(lambda: widget.filters == [expected_filter1], page)
    wait_until(lambda: widget.current_view.equals(expected_filter_df), page)

    str_header = page.locator('input[type="search"]')
    str_header.click()
    val, cmp, col = 'A', 'like', 'str'
    str_header.fill(val)
    str_header.press('Enter')
    query2 = f'{col} == {val!r}'
    expected_filter_df = df_mixed.query(f'{query1} and {query2}')
    expected_filter2 = {'field': col, 'type': cmp, 'value': val}
    expect(page.locator('.tabulator-row')).to_have_count(len(expected_filter_df))
    wait_until(lambda: widget.filters == [expected_filter1, expected_filter2], page)
    wait_until(lambda: widget.current_view.equals(expected_filter_df), page)


def test_tabulator_download(page, port, df_mixed, df_mixed_as_string):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check that the whole table content is on the page, just
    # to make sure the page is loaded before triggering the
    # download.
    table = page.locator('.tabulator')
    expect(table).to_have_text(
        df_mixed_as_string,
        use_inner_text=True
    )

    # Start waiting for the download
    with page.expect_download() as download_info:
        widget.download()
    download = download_info.value
    # Wait for the download process to complete
    path = download.path()

    saved_df = pd.read_csv(path, index_col='index')
    # Some transformations required to reform the dataframe as the original one.
    saved_df['date'] = pd.to_datetime(saved_df['date'], unit='ms')
    saved_df['date'] = saved_df['date'].astype(object)
    saved_df['datetime'] = pd.to_datetime(saved_df['datetime'], unit='ms')
    saved_df.index.name = None

    pd.testing.assert_frame_equal(df_mixed, saved_df)


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
    widget = Tabulator(df_mixed, configuration={'columnDefaults': {'headerSort': False}})

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

    wait_until(lambda: len(events) == 0, page)


@pytest.mark.parametrize('col', ['index', 'int', 'float', 'str', 'date', 'datetime'])
@pytest.mark.parametrize('dir', ['ascending', 'descending'])
def test_tabulator_sorters_on_init(page, port, df_mixed, col, dir):
    dir_ = 'asc' if dir == 'ascending' else 'desc'
    widget = Tabulator(df_mixed, sorters=[{'field': col, 'dir': dir_}])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    sorted_header = page.locator(f'[aria-sort="{dir}"]:visible')
    expect(sorted_header).to_have_attribute('tabulator-field', col)

    ascending = dir == 'ascending'
    if col == 'index':
        expected_current_view = df_mixed.sort_index(ascending=ascending)
    else:
        expected_current_view = df_mixed.sort_values(col, ascending=ascending)
    assert widget.current_view.equals(expected_current_view)


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3657')
def test_tabulator_sorters_on_init_multiple(page, port):
    df = pd.DataFrame({
        'col1': [1, 2, 3, 4],
        'col2': [1, 4, 3, 2],
    })
    sorters = [{'field': 'col1', 'dir': 'desc'}, {'field': 'col2', 'dir': 'asc'}]
    widget = Tabulator(df, sorters=sorters)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    s1 = page.locator('[aria-sort="descending"]:visible')
    expect(s1).to_have_attribute('tabulator-field', 'col1')
    s2 = page.locator('[aria-sort="ascending"]:visible')
    expect(s2).to_have_attribute('tabulator-field', 'col2')

    first_index_rendered = page.locator('.tabulator-cell:visible').first.inner_text()
    df_sorted = df.sort_values('col1', ascending=True).sort_values('col2', ascending=False)
    expected_first_index = df_sorted.index[0]

    # This fails
    assert int(first_index_rendered) == expected_first_index


def test_tabulator_sorters_set_after_init(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    widget.sorters = [{'field': 'int', 'dir': 'desc'}]

    sheader = page.locator('[aria-sort="descending"]:visible')
    expect(sheader).to_have_count(1)
    assert sheader.get_attribute('tabulator-field') == 'int'

    expected_df_sorted = df_mixed.sort_values('int', ascending=False)

    assert widget.current_view.equals(expected_df_sorted)


def test_tabulator_sorters_from_client(page, port, df_mixed):
    widget = Tabulator(df_mixed)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.locator('.tabulator-col', has_text='float').locator('.tabulator-col-sorter').click()

    sheader = page.locator('[aria-sort="ascending"]:visible')
    expect(sheader).to_have_count(1)
    assert sheader.get_attribute('tabulator-field') == 'float'

    wait_until(lambda: widget.sorters == [{'field': 'float', 'dir': 'asc'}], page)

    expected_df_sorted = df_mixed.sort_values('float', ascending=True)
    assert widget.current_view.equals(expected_df_sorted)


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3658')
def test_tabulator_sorters_pagination_no_page_reset(page, port, df_mixed):
    widget = Tabulator(df_mixed, pagination='remote', page_size=2)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.locator('text="Next"').click()

    expect(page.locator('text="idx2"')).to_have_count(1)

    widget.sorters = [{'field': 'float', 'dir': 'asc'}]

    page.locator('.tabulator-col', has_text='index').locator('.tabulator-col-sorter').click()

    # This fails, explicit timeout required
    page.wait_for_timeout(500)
    expect(page.locator('text="idx2"')).to_have_count(1, timeout=1000)
    assert widget.page == 2


@pytest.mark.parametrize('pagination', ['remote', 'local'])
def test_tabulator_sorters_pagination(page, port, df_mixed, pagination):
    widget = Tabulator(df_mixed, pagination=pagination, page_size=2)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")


    s = page.locator('.tabulator-col', has_text='str').locator('.tabulator-col-sorter')
    s.click()
    # Having to wait when pagination is set to remote before the next click,
    # maybe there's a better way.
    page.wait_for_timeout(100)
    s.click()

    sheader = page.locator('[aria-sort="descending"]:visible')
    expect(sheader).to_have_count(1)
    assert sheader.get_attribute('tabulator-field') == 'str'

    expected_sorted_df = df_mixed.sort_values('str', ascending=False)
    wait_until(lambda: widget.current_view.equals(expected_sorted_df), page)

    # Check that if we go to the next page the current_view hasn't changed
    page.locator('text="Next"').click()

    page.wait_for_timeout(200)
    wait_until(lambda: widget.current_view.equals(expected_sorted_df), page)


def test_tabulator_edit_event_sorters_not_automatically_applied(page, port, df_mixed):
    widget = Tabulator(df_mixed, sorters=[{'field': 'str', 'dir': 'desc'}])

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expected_vals = list(df_mixed['str'].sort_values(ascending=False))

    wait_until(lambda: tabulator_column_values(page, 'str') == expected_vals, page)

    # Chankge the cell that contains B to BB
    cell = page.locator('text="B"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("Z")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)

    expected_vals = [item if item != 'B' else 'Z' for item in expected_vals]
    wait_until(lambda: tabulator_column_values(page, 'str') == expected_vals, page)


def test_tabulator_click_event_and_header_filters(page, port):
    df = pd.DataFrame({
        'col1': list('ABCDD'),
        'col2': list('XXXXZ'),
    })
    widget = Tabulator(
        df,
        header_filters={'col1': {'type': 'input', 'func': 'like'}},
    )

    values = []
    widget.on_click(lambda e: values.append((e.column, e.row, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Set a filter on col1
    str_header = page.locator('input[type="search"]')
    str_header.click()
    str_header.fill('D')
    str_header.press('Enter')
    wait_until(lambda: len(widget.filters) == 1, page)

    # Click on the last cell
    cell = page.locator('text="Z"')
    cell.click()

    wait_until(lambda: len(values) == 1, page)
    # This cell was at index 4 in col2 of the original dataframe
    assert values[0] == ('col2', 4, 'Z')


def test_tabulator_edit_event_and_header_filters_last_row(page, port):
    df = pd.DataFrame({
        'col1': list('ABCDD'),
        'col2': list('XXXXZ'),
    })
    widget = Tabulator(
        df,
        header_filters={'col1': {'type': 'input', 'func': 'like'}},
    )

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Set a filter on col1
    str_header = page.locator('input[type="search"]')
    str_header.click()
    str_header.fill('D')
    str_header.press('Enter')
    wait_until(lambda: len(widget.filters) == 1, page)

    # Click on the last cell
    cell = page.locator('text="Z"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("ZZ")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)
    # This cell was at index 4 in col2 of the original dataframe
    assert values[0] == ('col2', 4, 'Z', 'ZZ')
    assert df['col2'].iloc[-1] == 'ZZ'
    assert widget.value.equals(df)
    assert widget.current_view.equals(df.query('col1 == "D"'))


def test_tabulator_edit_event_and_header_filters(page, port):
    df = pd.DataFrame({
        'col1': list('aaabcd'),
        'col2': list('ABCDEF')
    })
    widget = Tabulator(
        df,
        header_filters={'col1': {'type': 'input', 'func': 'like'}},
    )

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Set a filter on col1
    str_header = page.locator('input[type="search"]')
    str_header.click()
    str_header.fill('a')
    str_header.press('Enter')

    # Change the cell that contains B to BB
    cell = page.locator('text="B"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("BB")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)
    # This cell was at index 1 in col2 of the original dataframe
    assert values[0] == ('col2', 1, 'B', 'BB')
    assert df['col2'][1] == 'BB'
    assert widget.value.equals(df)
    assert widget.current_view.equals(df.query('col1 == "a"'))


@pytest.mark.flaky(max_runs=3)
def test_tabulator_edit_event_and_header_filters_same_column(page, port):
    df = pd.DataFrame({
        'values':  ['A', 'A', 'B', 'B'],
    }, index=['idx0', 'idx1', 'idx2', 'idx3'])

    widget = Tabulator(df, header_filters={'values': {'type': 'input', 'func': 'like'}})

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    header = page.locator('input[type="search"]')
    header.click()
    header.fill('B')
    header.press('Enter')

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(2)

    # Edit a cell in the filtered column, from B to X
    cell = page.locator('text="B"').nth(1)
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    # For some reason there's sometimes an edit event sent with the old
    # value as new value. Waiting here helps.
    page.wait_for_timeout(200)
    editable_cell.fill("X")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)
    assert values[0] == ('values', len(df) - 1, 'B', 'X')
    assert df.at['idx3', 'values'] == 'X'
    # The current view should show the edited value
    assert len(widget.current_view) == 2

    # In the same column, edit X to Y
    cell = page.locator('text="X"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("Y")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 2, page)
    assert values[-1] == ('values', len(df) - 1, 'X', 'Y')
    assert df.at['idx3', 'values'] == 'Y'
    assert len(widget.current_view) == 2

    # Edit the last B value found in that column, from B to Z
    cell = page.locator('text="B"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("Z")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 3, page)
    assert values[-1] == ('values', len(df) - 2, 'B', 'Z')
    assert df.at['idx2', 'values'] == 'Z'
    # current_view should show Y and Z, there's no more B
    assert len(widget.current_view) == 2


@pytest.mark.parametrize('pagination', ['remote', 'local'])
def test_tabulator_edit_event_and_header_filters_same_column_pagination(page, port, pagination):
    df = pd.DataFrame({
        'values':  ['A', 'A', 'B', 'B', 'B', 'B'],
    }, index=['idx0', 'idx1', 'idx2', 'idx3', 'idx4', 'idx5'])

    widget = Tabulator(
        df,
        header_filters={'values': {'type': 'input', 'func': 'like'}},
        pagination=pagination,
        page_size=2,
    )

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    header = page.locator('input[type="search"]')
    header.click()
    header.fill('B')
    header.press('Enter')

    wait_until(lambda: widget.current_view.equals(df[df['values'] == 'B']))

    cell = page.locator('text="B"').first
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("Q")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)
    assert values[-1] == ('values', 2, 'B', 'Q')
    assert df.at['idx2', 'values'] == 'Q'
    # current_view should show Y and Z, there's no more B
    assert len(widget.current_view) == 4

    page.locator('text="Last"').click()
    page.wait_for_timeout(200)

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(2)

    # Edit a cell in the filtered column, from B to X
    cell = page.locator('text="B"').nth(1)
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("X")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 2, page)
    assert values[-1] == ('values', len(df) - 1, 'B', 'X')
    assert df.at['idx5', 'values'] == 'X'
    # The current view should show the edited value
    assert len(widget.current_view) == 4

    # In the same column, edit X to Y
    cell = page.locator('text="X"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("Y")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 3, page)
    assert values[-1] == ('values', len(df) - 1, 'X', 'Y')
    assert df.at['idx5', 'values'] == 'Y'
    assert len(widget.current_view) == 4

    # Edit the last B value found in that column, from B to Z
    cell = page.locator('text="B"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("Z")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 4, page)
    assert values[-1] == ('values', len(df) - 2, 'B', 'Z')
    assert df.at['idx4', 'values'] == 'Z'
    # current_view should show Y and Z, there's no more B
    assert len(widget.current_view) == 4



@pytest.mark.parametrize('sorter', ['sorter', 'no_sorter'])
@pytest.mark.parametrize('python_filter', ['python_filter', 'no_python_filter'])
@pytest.mark.parametrize('header_filter', ['header_filter', 'no_header_filter'])
@pytest.mark.parametrize('pagination', ['remote', 'local', 'no_pagination'])
def test_tabulator_edit_event_integrations(page, port, sorter, python_filter, header_filter, pagination):
    sorter_col = 'col3'
    python_filter_col = 'col2'
    python_filter_val = 'd'
    header_filter_col = 'col1'
    header_filter_val = 'Y'
    target_col = 'col4'
    target_val = 'G'
    new_val = 'GG'

    df = pd.DataFrame({
        'col1': list('XYYYYYYZ'),
        'col2': list('abcddddd'),
        'col3': list(range(8)),
        'col4': list('ABCDEFGH')
    })

    target_index = df.set_index(target_col).index.get_loc(target_val)

    kwargs = {}
    if pagination != 'no_pagination':
        kwargs = dict(pagination=pagination, page_size=3)
    if header_filter == 'header_filter':
        kwargs.update(dict(header_filters={header_filter_col: {'type': 'input', 'func': 'like'}}))

    widget = Tabulator(df, **kwargs)

    if python_filter == 'python_filter':
        widget.add_filter(python_filter_val, python_filter_col)

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    if sorter == 'sorter':
        s = page.locator('.tabulator-col', has_text=sorter_col).locator('.tabulator-col-sorter')
        s.click()
        # Having to wait when pagination is set to remote before the next click,
        # maybe there's a better way.
        page.wait_for_timeout(200)
        s.click()
        page.wait_for_timeout(200)

    if header_filter == 'header_filter':
        str_header = page.locator('input[type="search"]')
        str_header.click()
        str_header.fill(header_filter_val)
        str_header.press('Enter')
        wait_until(lambda: len(widget.filters) == 1, page)

    if pagination != 'no_pagination' and sorter == 'no_sorter':
        page.locator('text="Last"').click()
        page.wait_for_timeout(200)

    # Change the cell concent
    cell = page.locator(f'text="{target_val}"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill(new_val)
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)
    assert values[0] == (target_col, target_index, target_val, new_val)
    assert df[target_col][target_index] == new_val
    assert widget.value.equals(df)
    if sorter == 'sorter':
        expected_current_view = widget.value.sort_values(sorter_col, ascending=False)
    else:
        expected_current_view = widget.value
    if python_filter == 'python_filter':
        expected_current_view = expected_current_view.query(f'{python_filter_col} == @python_filter_val')
    if header_filter == 'header_filter':
        expected_current_view = expected_current_view.query(f'{header_filter_col} == @header_filter_val')
    assert widget.current_view.equals(expected_current_view)


@pytest.mark.parametrize('sorter', ['sorter', 'no_sorter'])
@pytest.mark.parametrize('python_filter', ['python_filter', 'no_python_filter'])
@pytest.mark.parametrize('header_filter', ['header_filter', 'no_header_filter'])
@pytest.mark.parametrize('pagination', ['remote', 'local', 'no_pagination'])
def test_tabulator_click_event_selection_integrations(page, port, sorter, python_filter, header_filter, pagination):
    sorter_col = 'col3'
    python_filter_col = 'col2'
    python_filter_val = 'd'
    header_filter_col = 'col1'
    header_filter_val = 'Y'
    target_col = 'col4'
    target_val = 'G'

    df = pd.DataFrame({
        'col1': list('XYYYYYYZ'),
        'col2': list('abcddddd'),
        'col3': list(range(8)),
        'col4': list('ABCDEFGH')
    })

    target_index = df.set_index(target_col).index.get_loc(target_val)

    kwargs = {}
    if pagination != 'no_pagination':
        kwargs.update(dict(pagination=pagination, page_size=3))
    if header_filter == 'header_filter':
        kwargs.update(dict(header_filters={header_filter_col: {'type': 'input', 'func': 'like'}}))
    widget = Tabulator(df, disabled=True, **kwargs)

    if python_filter == 'python_filter':
        widget.add_filter(python_filter_val, python_filter_col)

    values = []
    widget.on_click(lambda e: values.append((e.column, e.row, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    if sorter == 'sorter':
        s = page.locator('.tabulator-col', has_text=sorter_col).locator('.tabulator-col-sorter')
        s.click()
        # Having to wait when pagination is set to remote before the next click,
        # maybe there's a better way.
        page.wait_for_timeout(200)
        s.click()
        page.wait_for_timeout(200)

    if header_filter == 'header_filter':
        str_header = page.locator('input[type="search"]')
        str_header.click()
        str_header.fill(header_filter_val)
        str_header.press('Enter')
        wait_until(lambda: len(widget.filters) == 1, page)

    if pagination != 'no_pagination' and sorter == 'no_sorter':
        page.locator('text="Last"').click()
        page.wait_for_timeout(200)

    # Click on the cell
    cell = page.locator(f'text="{target_val}"')
    cell.click()

    wait_until(lambda: len(values) == 1, page)
    assert values[0] == (target_col, target_index, target_val)
    target_selection_index = widget.current_view.index.get_loc(target_index)
    if python_filter == 'python_filter' or header_filter == 'header_filter' or sorter == 'sorter':
        pytest.xfail(reason='See https://github.com/holoviz/panel/issues/3664')
    wait_until(lambda: widget.selection == [target_selection_index], page)

    if header_filter == 'header_filter' or sorter == 'sorter' or (pagination == 'remote' and python_filter == 'python_filter'):
        pytest.xfail(reason='See https://github.com/holoviz/panel/issues/3664')
    expected_selected = df.iloc[[target_index], :]
    assert widget.selected_dataframe.equals(expected_selected)


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3664')
def test_tabulator_selection_sorters_on_init(page, port, df_mixed):
    widget = Tabulator(df_mixed, sorters=[{'field': 'int', 'dir': 'desc'}])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Click on the last index cell to select it
    last_index = df_mixed.index[-1]
    cell = page.locator(f'text="{last_index}"')
    cell.click()

    wait_until(lambda: widget.selection == [len(df_mixed) - 1], page)
    expected_selected = df_mixed.loc[[last_index], :]
    assert widget.selected_dataframe.equals(expected_selected)


@pytest.mark.xfail(reason='https://github.com/holoviz/panel/issues/3664')
def test_tabulator_selection_header_filter_unchanged(page, port):
    df = pd.DataFrame({
        'col1': list('XYYYYY'),
        'col2': list('abcddd'),
        'col3': list('ABCDEF')
    })
    selection = [2, 3]
    widget = Tabulator(
        df,
        selection=selection,
        header_filters={'col1': {'type': 'input', 'func': 'like'}}
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    str_header = page.locator('input[type="search"]')
    str_header.click()
    str_header.fill('Y')
    str_header.press('Enter')
    page.wait_for_timeout(300)

    assert widget.selection == selection
    expected_selected = df.iloc[selection, :]
    assert widget.selected_dataframe.equals(expected_selected)


@pytest.mark.xfail(reason='See https://github.com/holoviz/panel/issues/3670')
def test_tabulator_selection_header_filter_changed(page, port):
    df = pd.DataFrame({
        'col1': list('XYYYYY'),
        'col2': list('abcddd'),
        'col3': list('ABCDEF')
    })
    selection = [0, 3]
    widget = Tabulator(
        df,
        selection=selection,
        header_filters={'col1': {'type': 'input', 'func': 'like'}}
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    str_header = page.locator('input[type="search"]')
    str_header.click()
    str_header.fill('Y')
    str_header.press('Enter')
    page.wait_for_timeout(300)

    assert widget.selection == selection
    expected_selected = df.iloc[selection, :]
    assert widget.selected_dataframe.equals(expected_selected)


def test_tabulator_loading_no_horizontal_rescroll(page, port, df_mixed):
    widths = 100
    width = int(((df_mixed.shape[1] + 1) * widths) / 2)
    df_mixed['Target'] = 'target'
    widget = Tabulator(df_mixed, width=width, widths=widths)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    cell = page.locator('text="target"').first
    # Scroll to the right
    cell.scroll_into_view_if_needed()
    page.wait_for_timeout(200)
    bb = page.locator('text="Target"').bounding_box()

    widget.loading = True
    page.wait_for_timeout(200)
    widget.loading = False

    # To catch a potential rescroll
    page.wait_for_timeout(400)
    # The table should keep the same scroll position
    assert bb == page.locator('text="Target"').bounding_box()


def test_tabulator_loading_no_vertical_rescroll(page, port):
    arr = np.array(['a'] * 10)

    arr[-1] = 'T'
    df = pd.DataFrame({'col': arr})
    height, width = 200, 200
    widget = Tabulator(df, height=height, width=width)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Scroll to the bottom, and give it a little extra time
    page.locator('text="T"').scroll_into_view_if_needed()
    page.wait_for_timeout(200)

    bb = page.locator('text="T"').bounding_box()

    widget.loading = True
    page.wait_for_timeout(200)
    widget.loading = False

    # To catch a potential rescroll
    page.wait_for_timeout(400)
    # The table should keep the same scroll position
    assert bb == page.locator('text="T"').bounding_box()


def test_tabulator_trigger_value_update(page, port):
    # Checking that this issue is resolved:
    # https://github.com/holoviz/panel/issues/3695
    nrows = 25
    df = pd.DataFrame(np.random.rand(nrows, 2), columns=['a', 'b'])
    widget = Tabulator(df)

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    expect(page.locator('.tabulator-row')).to_have_count(nrows)
    widget.param.trigger('value')
    page.wait_for_timeout(200)
    # This currently fails because of a Tabulator JS issue,
    # it only displays the first 20 rows.
    expect(page.locator('.tabulator-row')).to_have_count(nrows)


@pytest.mark.parametrize('pagination', ['remote', 'local'])
def test_tabulator_selection_header_filter_pagination_updated(page, port, df_mixed, pagination):
    widget = Tabulator(
        df_mixed,
        header_filters={'str': {'type': 'input', 'func': 'like'}},
        pagination=pagination,
        page_size=3,
    )

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    page.locator('text="Last"').click()
    wait_until(lambda: widget.page == 2, page)

    str_header = page.locator('input[type="search"]')
    str_header.click()
    str_header.fill('D')
    str_header.press('Enter')

    wait_until(lambda: widget.page == 1, page)


def test_tabulator_sort_algorithm(page, port):
    df = pd.DataFrame({
        'vals': [
            'A',
            'i',
            'W',
            'g',
            'r',
            'l',
            'a',
            'n',
            'z',
            'N',
            'a',
            'l',
            's',
            'm',
            'J',
            'C',
            'w'
        ],
        'groups': [
            'A',
            'B',
            'C',
            'B',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'A',
            'A'
        ],
    })
    target_col = 'vals'

    widget = Tabulator(df, sorters=[{'field': 'groups', 'dir': 'asc'}])

    values = []
    widget.on_click(lambda e: values.append((e.column, e.row, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Click on the cell
    target_val = 'i'
    target_index = df.set_index(target_col).index.get_loc(target_val)
    cell = page.locator(f'text="{target_val}"')
    cell.click()

    wait_until(lambda: len(values) == 1, page)
    assert values[0] == (target_col, target_index, target_val)

    # Click on the cell
    target_val = 'W'
    target_index = df.set_index(target_col).index.get_loc(target_val)
    cell = page.locator(f'text="{target_val}"')
    cell.click()

    wait_until(lambda: len(values) == 2, page)
    assert values[1] == (target_col, target_index, target_val)


def test_tabulator_sort_algorithm_no_show_index(page, port):
    df = pd.DataFrame({
        'vals': [
            'A',
            'i',
            'W',
            'g',
            'r',
            'l',
            'a',
            'n',
            'z',
            'N',
            'a',
            'l',
            's',
            'm',
            'J',
            'C',
            'w'
        ],
        'groups': [
            'A',
            'B',
            'C',
            'B',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'C',
            'A',
            'A'
        ],
    }, index=np.random.choice(list(range(17)), size=17, replace=False))
    target_col = 'vals'

    widget = Tabulator(df, sorters=[{'field': 'groups', 'dir': 'asc'}], show_index=False)

    values = []
    widget.on_click(lambda e: values.append((e.column, e.row, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Click on the cell
    target_val = 'i'
    target_index = df.set_index(target_col).index.get_loc(target_val)
    cell = page.locator(f'text="{target_val}"')
    cell.click()

    wait_until(lambda: len(values) == 1, page)
    assert values[0] == (target_col, target_index, target_val)

    # Click on the cell
    target_val = 'W'
    target_index = df.set_index(target_col).index.get_loc(target_val)
    cell = page.locator(f'text="{target_val}"')
    cell.click()

    wait_until(lambda: len(values) == 2, page)
    assert values[1] == (target_col, target_index, target_val)


@pytest.mark.parametrize(
    ('col', 'vals'),
    (
        ('string', [np.nan, '', 'B', 'a', '', np.nan]),
        ('number', [1.0, 1.0, 0.0, 0.0]),
        ('boolean', [True, True, False, False]),
        ('datetime', [dt.datetime(2019, 1, 1, 1), np.nan, dt.datetime(2019, 12, 1, 1), dt.datetime(2019, 12, 1, 1), np.nan, dt.datetime(2019, 6, 1, 1), np.nan])
    ),
)
def test_tabulator_sort_algorithm_by_type(page, port, col, vals):
    df = pd.DataFrame({
        col: vals,
    })

    widget = Tabulator(df, sorters=[{'field': col, 'dir': 'asc'}])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Attempt at making this test more robust.
    page.wait_for_timeout(200)

    client_index = [int(i) for i in tabulator_column_values(page, 'index')]

    def indexes_equal():
        assert client_index == list(widget.current_view.index)

    wait_until(indexes_equal, page)


def test_tabulator_python_filter_edit(page, port):
    df = pd.DataFrame({
        'values':  ['A', 'A', 'B', 'B'],
    }, index=['idx0', 'idx1', 'idx2', 'idx3'])

    widget = Tabulator(df)

    fltr, col = 'B', 'values'
    widget.add_filter(fltr, col)

    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    # Check the table has the right number of rows
    expect(page.locator('.tabulator-row')).to_have_count(2)

    cell = page.locator('text="B"').nth(1)
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("X")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)
    assert values[0] == ('values', len(df) - 1, 'B', 'X')
    assert df.at['idx3', 'values'] == 'X'

    cell = page.locator('text="X"')
    cell.click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill("Y")
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 2, page)
    assert values[-1] == ('values', len(df) - 1, 'X', 'Y')
    assert df.at['idx3', 'values'] == 'Y'


def test_tabulator_sorter_default_number(page, port):
    df = pd.DataFrame({'x': []}).astype({'x': int})
    widget = Tabulator(df, sorters=[{"field": "x", "dir": "desc"}])

    serve(widget, port=port, threaded=True, show=False)

    time.sleep(0.2)

    page.goto(f"http://localhost:{port}")

    df2 = pd.DataFrame({'x': [0, 96, 116]})
    widget.value = df2

    def x_values():
        table_values = [int(v) for v in tabulator_column_values(page, 'x')]
        assert table_values == list(df2['x'].sort_values(ascending=False))

    wait_until(x_values, page)
