import pytest

pytest.importorskip('playwright')

from playwright.sync_api import expect

from panel.tests.util import serve_component, wait_until
from panel.widgets import (
    AutocompleteInput, MultiSelect, NestedSelect, Select,
)

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

    wait_until(lambda: bool(clicks) and clicks[0].option == 'B', page)


def test_nested_select_update_options(page):
    n = NestedSelect(options={"a": {"b": ["c", "d"]}})

    serve_component(page, n)

    expect(page.locator('option').first).to_have_text("a")

    n.options = {"c": {"d": ["e", "f"]}}
    expect(page.locator('option').first).to_have_text("c")


def test_autocomplete_max_completions(page):
    widget = AutocompleteInput(
        options=[f'Alpha{i:02d}' for i in range(20)],
        max_completions=3, min_characters=1,
    )
    serve_component(page, widget)

    field = page.locator('input')
    model_id = next(iter(widget._models.values()))[0].id
    field.press_sequentially('Al')
    matches = page.locator('.bk-menu > div')
    expect(matches).to_have_count(3)
    expect(matches.nth(2)).to_have_text('Alpha02')
    matches.nth(2).click()
    wait_until(lambda: widget.value == 'Alpha02', page)

    widget.max_completions = 5
    page.wait_for_function(
        f"Bokeh.documents[0].get_model_by_id('{model_id}').max_completions === 5"
    )
    field.fill('')
    field.press_sequentially('Al')
    expect(matches).to_have_count(5)

    widget.max_completions = None
    page.wait_for_function(
        f"Bokeh.documents[0].get_model_by_id('{model_id}').max_completions === null"
    )
    field.fill('')
    field.press_sequentially('Al')
    expect(matches).to_have_count(20)
