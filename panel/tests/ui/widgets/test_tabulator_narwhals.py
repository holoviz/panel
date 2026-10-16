"""
Round-trip checks for Tabulator with DataFrames without an index. The
frontend is identical to the pandas case, so the remaining behavior is
covered by unit tests in panel/tests/widgets/test_tables_narwhals.py.
"""
import pytest

pytest.importorskip("playwright")

from panel.tests.util import serve_component, wait_until
from panel.util.dataframe import to_narwhals
from panel.widgets import Tabulator

pl = pytest.importorskip('polars')
pa = pytest.importorskip('pyarrow')

pytestmark = pytest.mark.ui

DATA = {
    'int': [1, 2, 3, 4],
    'float': [3.14, 6.28, 9.42, -2.45],
    'str': ['A', 'B', 'C', 'D'],
}


@pytest.fixture(params=[pl.DataFrame, pa.table], ids=['polars', 'pyarrow'])
def frame(request):
    return request.param(DATA)


def column(df, col):
    return to_narwhals(df)[col].to_list()


def rendered(page, col):
    return page.locator(f'[tabulator-field={col}][role=gridcell]').all_inner_texts()


def test_tabulator_indexless_edit_sorted(page, frame):
    widget = Tabulator(frame, sorters=[{'field': 'int', 'dir': 'desc'}])
    values = []
    widget.on_edit(lambda e: values.append((e.column, e.row, e.old, e.value)))

    serve_component(page, widget)

    wait_until(lambda: rendered(page, 'str') == ['D', 'C', 'B', 'A'], page)
    page.locator('text="D"').click()
    editable_cell = page.locator('input[type="text"]')
    editable_cell.fill('DD')
    editable_cell.press('Enter')

    wait_until(lambda: len(values) == 1, page)
    assert values[0] == ('str', 3, 'D', 'DD')
    assert type(widget.value) is type(frame)
    assert column(widget.value, 'str') == ['A', 'B', 'C', 'DD']


def test_tabulator_indexless_selection(page, frame):
    widget = Tabulator(frame, disabled=True, sorters=[{'field': 'int', 'dir': 'desc'}])

    serve_component(page, widget)

    wait_until(lambda: rendered(page, 'str') == ['D', 'C', 'B', 'A'], page)
    page.locator('text="C"').click()

    wait_until(lambda: widget.selection == [2], page)
    assert column(widget.selected_dataframe, 'str') == ['C']
