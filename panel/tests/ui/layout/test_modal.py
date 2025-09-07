import pytest

from panel.layout import Modal, Spacer
from panel.tests.util import serve_component

pytest.importorskip("playwright")

from playwright.sync_api import expect

pytestmark = pytest.mark.ui


def test_modal_close_open(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_hidden()

    modal.open = True
    expect(modal_locator).to_be_visible()


def test_modal_open_close(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
        open=True,
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_visible()

    page.mouse.click(0, 0)
    expect(modal_locator).to_be_hidden()


@pytest.mark.parametrize("show_close_button", [True, False])
def test_modal_show_close_button(page, show_close_button):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
        open=True,
        show_close_button=show_close_button,
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_visible()

    modal_locator = page.locator("#pnx_dialog_close")
    if show_close_button:
        expect(modal_locator).to_be_visible()
    else:
        expect(modal_locator).to_be_hidden()


def test_modal_background_close(page):
    modal = Modal(
        Spacer(styles=dict(background="red"), width=200, height=200),
        Spacer(styles=dict(background="green"), width=200, height=200),
        Spacer(styles=dict(background="blue"), width=200, height=200),
        open=True,
        background_close=False,
    )

    serve_component(page, modal)

    modal_locator = page.locator("#pnx_dialog_content")
    expect(modal_locator).to_be_visible()

    # Should still be visible
    page.mouse.click(0, 0)
    expect(modal_locator).to_be_visible()
