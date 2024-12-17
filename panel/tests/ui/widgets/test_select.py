import pytest

from panel.tests.util import serve_component, wait_until
from panel.widgets import MultiSelect, Select

pytestmark = pytest.mark.ui


def test_select_with_size(page):
    select = Select(options=['A', 'B', 'C'], size=4)

    serve_component(page, select)

    page.locator('option').nth(1).click()

    wait_until(lambda: select.value == 'B')

def test_select_option(page):
    select = Select(value='B', options=['A', 'B', 'C'], size=4)

    serve_component(page, select)

    wait_until(lambda: page.locator('select').evaluate("(sel)=>sel.value") == 'B', page)

def test_multi_select_double_click(page):
    clicks = []
    select = MultiSelect(options=['A', 'B', 'C'], on_double_click=clicks.append)

    serve_component(page, select)

    page.locator('option').nth(1).dblclick()

    wait_until(lambda: bool(clicks) and clicks[0].option == 'B')
