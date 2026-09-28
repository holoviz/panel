import pytest

from panel.tests.util import serve_component, wait_until

pytest.importorskip("playwright")

from playwright.sync_api import expect

pytestmark = pytest.mark.ui


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
